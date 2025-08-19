import asyncio
import fsspec

from typing import List, Optional, Type
from tenacity import retry, stop_after_attempt, wait_random, retry_if_exception_type
from tqdm.asyncio import tqdm

from dxtrx.utils.hash import hash_object_sha256
from dxtrx.utils.ml.llm.prompt import format_prompt
from dxtrx.utils.cache.gcs import GCSCache

class SchemaMapper:
    def __init__(
        self,
        *,
        agent_prompt,
        output_schema: Type,
        openai_client,
        limiter,
        max_response_tokens=1024,
        model="gpt-4o-mini",
        temperature=0.2,
        compression="gzip", 
        cache_root=None,
        if_cache_present="return",
        openai_user="dxtr_llm"
    ):
        self.agent_prompt = agent_prompt
        self.output_schema = output_schema
        self.openai_client = openai_client
        self.openai_user = openai_user
        self.limiter = limiter
        
        self.cache_root = (
            f"{cache_root}/"
            f"model={model}/"
            f"temperature={temperature}/"
            f"response_format={output_schema.__name__}"
        )
        
        self.fs = fsspec.filesystem("gs")
        self.cache = GCSCache(self.fs, compression=compression, cache_root=self.cache_root)
        
        if compression == "gzip":
            self.suffix = "json.gz"
        elif compression == "bz2":
            self.suffix = "json.bz2"
        else:
            raise ValueError(f"Unsupported compression: {compression}")
        
        self.max_response_tokens = max_response_tokens
        self.model = model
        self.temperature = temperature
        
        if if_cache_present not in ["return", "overwrite"]:
            raise ValueError(f"Invalid value for if_cache_present: {if_cache_present}")
        self.if_cache_present = if_cache_present

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_random(min=10, max=60),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def call_llm_with_retry(self, params):
        return await self.openai_client.beta.chat.completions.parse(**params)

    async def map_single(self, variables: dict, semaphore: asyncio.Semaphore) -> Optional[object]:
        result_prompt = format_prompt(self.agent_prompt, variables)
        hash_str = hash_object_sha256(variables, normalize=False)
        path = f"{hash_str}.{self.suffix}"
        
        try:
            response = await self.cache.read(path)
            
            if self.if_cache_present == "return":
                return self.output_schema.model_validate_json(
                    response["choices"][0]["message"]["content"]
                )
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ Cache read error for {variables.get('product', '???')}: {e}")

        async with semaphore:
            try:
                await self.limiter.acquire(result_prompt.messages, max_response_tokens=self.max_response_tokens)
                params = {
                    "model": self.model,
                    "messages": result_prompt.messages,
                    "temperature": self.temperature,
                    "response_format": self.output_schema,
                    "max_tokens": self.max_response_tokens,
                    "user": self.openai_user
                }
                response = await self.call_llm_with_retry(params)
                obj = self.output_schema.model_validate_json(
                    response.choices[0].message.content
                )

                try:
                    await self.cache.write(path, response.model_dump())
                except Exception as e:
                    print(f"⚠️ Cache write error: {e}")

                return obj
            except Exception as e:
                print(f"❌ LLM error for {variables.get('product', '???')}: {e}")
                return {"error": str(e)}

    async def map_all(self, input_list: List[dict], max_concurrent: int = 5) -> List[Optional[object]]:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create indexed tasks that return (index, result) tuples
        async def indexed_map(i, vars_):
            res = await self.map_single(vars_, semaphore)
            return (i, res)
        
        tasks = [indexed_map(i, vars_) for i, vars_ in enumerate(input_list)]
        
        # Process tasks as they complete, storing results by index
        results_dict = {}
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Mapping"):
            try:
                i, res = await coro
                results_dict[i] = res
            except Exception as e:
                print(f"❌ Error in task: {e}")
                # Find the index of the failed task
                for j, task in enumerate(tasks):
                    if task == coro:
                        results_dict[j] = None
                        break
        
        # Reassemble results in original input order
        results = [results_dict[i] for i in range(len(input_list))]
        return results

    def run(self, input_list: List[dict], max_concurrent: int = 5) -> List[Optional[object]]:
        return asyncio.run(self.map_all(input_list, max_concurrent=max_concurrent))

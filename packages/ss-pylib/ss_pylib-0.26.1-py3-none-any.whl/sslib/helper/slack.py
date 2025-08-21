import httpx


class Slack:
  def __init__(self, webHook:str):
    self.__webHook = webHook
    
  async def async_send_message(self, message:str) -> bool:
    async with httpx.AsyncClient() as client:
      res = await client.post(self.__webHook, json={'text':message})
      return True if res.status_code == httpx.codes.OK else False
    
  def send_message(self, message:str) -> bool:
    res = httpx.post(self.__webHook, json={'text':message})
    return True if res.status_code == httpx.codes.OK else False
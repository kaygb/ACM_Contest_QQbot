import httpx
import asyncio


async def get_html(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close'
    }

    # r = requests.get(url=url, headers=headers)
    async with httpx.AsyncClient() as client:
        r = await client.get(url=url, headers=headers)

    # r.encoding = r.apparent_encoding
    # await asyncio.sleep(5)
    return r.text


async def get_json(url):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        'Connection': 'close'
    }

    # response = requests.get(url=url, headers=headers)
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    # print(response.status_code)

    try:
        # url_text = response.content.decode()
        # print(url_text)
        # json_data = json.loads(url_text)
        json_data = response.json()
        # await asyncio.sleep(5)
        return json_data
    except:
        return -1


async def text_save(filename, text):  # filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename, 'w', encoding='UTF-8')
    file.write(text)
    file.close()
    print("保存文件成功")
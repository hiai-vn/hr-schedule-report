# Lỗi: asyncio.run() cannot be called from a running event loop

## Mô tả lỗi

```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

## Nguyên nhân

Lỗi xảy ra khi sử dụng `asyncio.run()` bên trong một event loop đang chạy. Trong Python, chỉ có thể có **một event loop chạy tại một thời điểm** trong mỗi thread.

### Ví dụ gây lỗi

```python
from pocketflow import Node

class FetchTelegramMessagesNode(Node):  # Node đồng bộ
    def exec(self, params):
        # Lỗi: gọi asyncio.run() trong khi flow đang chạy async
        return asyncio.run(self._fetch_messages_async(params))
```

Khi `AsyncFlow.run_async()` được gọi, nó đã khởi tạo một event loop. Nếu một node con gọi `asyncio.run()`, Python sẽ báo lỗi vì không thể tạo event loop lồng nhau.

## Cách khắc phục

Chuyển đổi `Node` thành `AsyncNode` và sử dụng các phương thức async tương ứng:

| Node (sync)     | AsyncNode (async)       |
|-----------------|-------------------------|
| `prep()`        | `prep_async()`          |
| `exec()`        | `exec_async()`          |
| `post()`        | `post_async()`          |

### Code đã sửa

```python
from pocketflow import AsyncNode

class FetchTelegramMessagesNode(AsyncNode):  # Đổi thành AsyncNode
    async def prep_async(self, shared):  # Đổi thành prep_async
        now = datetime.now(timezone.utc)
        return {
            "year": now.year,
            "month": now.month
        }

    async def exec_async(self, params):  # Đổi thành exec_async
        # Dùng await thay vì asyncio.run()
        return await self._fetch_messages_async(params)

    async def post_async(self, shared, prep_res, exec_res):  # Đổi thành post_async
        shared["telegram_messages_csv"] = exec_res
        return "default"
```

## Quy tắc chung

1. **Nếu flow là `AsyncFlow`**: Các node có async code nên dùng `AsyncNode`
2. **Không bao giờ** gọi `asyncio.run()` bên trong một async function hoặc khi event loop đang chạy
3. **Dùng `await`** thay vì `asyncio.run()` khi đã ở trong context async

## Cách phát hiện

Kiểm tra call stack trong error message:
- Nếu thấy `run_async`, `_orch_async`, `asyncio.runners` → đang trong async context
- Nếu node gọi `asyncio.run()` → đây là nguồn gốc lỗi

## Tham khảo

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [PocketFlow AsyncNode](pocketflow.py)
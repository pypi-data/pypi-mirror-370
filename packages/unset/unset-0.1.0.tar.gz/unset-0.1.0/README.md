## unset

一个用于区分“未设置/未提供”与“显式提供 None/False”的 Python 单例哨兵值：`Unset`。

### 特性

- 单例实现：全局仅一个实例 `Unset`
- 语义清晰：`repr(Unset) -> "Unset"`，`bool(Unset) -> False`
- 便捷检查：`Unset(value)` 等价于 `value is Unset`
- 复制与深拷贝安全：`copy(Unset)` 与 `deepcopy(Unset)` 都返回自身
- Pydantic v2 友好：内置 `pydantic-core` schema 支持（可与 `pydantic>=2` 协同）

### 安装

```shell
python -m pip install --upgrade unset
```

依赖：`pydantic-core>=2,<3`。

### 快速示例

```python
from unset import Unset

def update_user(email=Unset):
    if email is Unset:
        return "no change"  # 调用方未传入 email
    if email is None:
        return "clear"      # 调用方显式传入 None
    return f"set to {email}"

assert bool(Unset) is False
assert Unset(Unset) is True  # 等价于 `Unset is Unset`
```

#### 与 None 的区别

- `Unset` 表示“未提供/未设置”。
- `None` 表示“显式提供空值”。

这在“部分更新接口”、“差异合并逻辑”、“默认参数”场景中非常有用。

### 与 Pydantic v2 集成（可选）

若安装了 `pydantic>=2`，可以直接在模型中使用 `Unset`：

```python
from pydantic import BaseModel
from unset import Unset, UnsetType

class PatchUser(BaseModel):
    email: UnsetType | str | None = Unset

payload = PatchUser()  # email == Unset
```

注意：本项目仅依赖 `pydantic-core`；如需使用 `BaseModel`，请额外安装 `pydantic>=2`。

### 许可

MIT License

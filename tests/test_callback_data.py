import pytest
from typing import Optional, Literal
from pydantic import ValidationError
import json
from eiogram.utils.callback_data import CallbackData
from eiogram.types._callback_query import CallbackQuery
from eiogram.types._user import User

class SimpleAction(CallbackData, prefix="simple"):
    action: str
    item_id: int

class ComplexAction(CallbackData, prefix="complex"):
    action_type: Literal["create", "update", "delete"]
    user_id: int
    is_admin: bool = False
    metadata: Optional[dict] = None

class OptionalFields(CallbackData, prefix="optional"):
    required: str
    optional: Optional[str] = None
    nullable: Optional[int] = None

def test_simple_pack_unpack():
    action = SimpleAction(action="delete", item_id=42)
    packed = action.pack()
    assert packed == "simple:delete:42"
    
    unpacked = SimpleAction.unpack(packed)
    assert unpacked.action == "delete"
    assert unpacked.item_id == 42

def test_default_values():
    action = ComplexAction(action_type="create", user_id=1)
    assert action.is_admin is False
    assert action.metadata is None
    
    packed = action.pack()
    assert packed == "complex:create:1:False:"

    unpacked = ComplexAction.unpack(packed)
    assert unpacked.action_type == "create"
    assert unpacked.is_admin is False

def test_optional_fields():
    opt1 = OptionalFields(required="value")
    assert opt1.optional is None
    assert opt1.nullable is None
    
    unpacked = OptionalFields.unpack("optional:value::123")
    assert unpacked.required == "value"
    assert unpacked.optional is None
    assert unpacked.nullable == 123

def test_validation():
    with pytest.raises(ValidationError):
        SimpleAction(action="delete", item_id="not_an_integer")
    
    with pytest.raises(ValidationError):
        ComplexAction(action_type="invalid", user_id=1)
    
    with pytest.raises(ValidationError):
        OptionalFields()

def test_invalid_format():
    with pytest.raises(ValueError, match="Invalid callback_data format"):
        SimpleAction.unpack("wrong_prefix:delete:42")
    
    with pytest.raises(ValueError):
        SimpleAction.unpack("simple:delete")

def test_filters():
    user = User(id=1, is_bot=False, first_name="Test")
    callback1 = CallbackQuery(id="123", from_user=user, data="simple:view:123")
    
    filter1 = SimpleAction.filter(action="view")
    assert filter1._filter_func(callback1) is not False

def test_special_values():
    action = ComplexAction(action_type="delete", user_id=1, is_admin=True)
    packed = action.pack()
    assert packed == "complex:delete:1:True:"
    
    metadata = {"key": "value"}
    action2 = ComplexAction(action_type="update", user_id=2, metadata=metadata)
    packed2 = action2.pack()
    assert json.dumps(metadata) in packed2

def test_null_empty_values():
    unpacked = OptionalFields.unpack("optional:value::123")
    assert unpacked.required == "value"
    assert unpacked.optional is None
    assert unpacked.nullable == 123
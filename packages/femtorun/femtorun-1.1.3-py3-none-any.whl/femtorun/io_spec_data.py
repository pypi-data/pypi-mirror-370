from typing import *

OPTIONAL_KEYS = ["comments", "quantization"]


class IOSpecQuant(TypedDict):
    scale: float
    zero_pt: float


class IOSpecInout(TypedDict):
    type: Literal["input", "output"]
    varname: str
    length: int
    precision: int
    padded_length: int
    quantization: IOSpecQuant
    comments: Dict[str, str]


class IOSpecSimpleSequence(TypedDict):
    type: Literal["simple_sequence"]
    outputs: List[str]
    inputs: List[str]
    comments: Dict[str, str]


class IOSpecComplexSequence(TypedDict):
    type: Literal["complex_sequence"]
    outputs: Dict[str, int]
    inputs: Dict[str, int]
    comments: Dict[str, str]


IOSpecData = Dict[str, Union[IOSpecInout, IOSpecSimpleSequence, IOSpecComplexSequence]]


def _check_TypedDict(D, TypedDictCls):
    # check if needed keys present
    # doesn't check if there are extra keys
    for k, objtype in TypedDictCls.__annotations__.items():
        if k not in OPTIONAL_KEYS:
            if k not in D:
                raise ValueError(f"{TypedDictCls.__name__} requires key {k}")
            if objtype in [str, int, float]:
                if not isinstance(D[k], objtype):
                    raise ValueError(
                        f"{TypedDictCls.__name__} requires key {k} to be of type {objtype}, saw {type(D[k])}"
                    )
            elif objtype == List[str]:
                ok = [isinstance(el, str) for el in D[k]]
                if not all(ok):
                    raise ValueError(
                        f"{TypedDictCls.__name__} requires key {k} to be list of str, saw something else"
                    )
            elif objtype == Dict[str, str]:
                ok = [
                    isinstance(k, int) and isinstance(v, int) for k, v in D[k].items()
                ]
                if not all(ok):
                    raise ValueError(
                        f"{TypedDictCls.__name__} requires key {k} to be Dict[str:int], saw something else"
                    )
            elif objtype == IOSpecQuant:
                _check_TypedDict(D[k], IOSpecQuant)


def check_IOSpecData(data: IOSpecData):
    """checks that all keys are present
    no comprehensive type checking yet
    """
    for objname, obj in data.items():
        if obj["type"] in ["input", "output"]:
            _check_TypedDict(obj, IOSpecInout)
        elif obj["type"] == "simple_sequence":
            _check_TypedDict(obj, IOSpecSimpleSequence)
        elif obj["type"] == "complex_sequence":
            _check_TypedDict(obj, IOSpecComplexSequence)
        else:
            raise ValueError(f"IO spec entry {objname} had undefined type")

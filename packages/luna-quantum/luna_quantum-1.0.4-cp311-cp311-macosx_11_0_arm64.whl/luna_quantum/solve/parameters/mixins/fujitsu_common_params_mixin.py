from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class FujitsuCommonParamsMixin(BaseModel):
    """
    Common parameters used across various quantum and classical optimization solvers.

    This class encapsulates parameters for auto-tuning, scaling, and general
    configuration options that are applicable to multiple solver types. It provides a
    consistent interface for these common settings to simplify configuration and
    enhance reusability.

    Attributes
    ----------
    auto_tuning: Literal["NOTHING", "SCALING", "AUTO_SCALING", "SAMPLING",
                        "AUTO_SCALING_AND_SAMPLING", "SCALING_AND_SAMPLING"]
        Controls automatic parameter adjustment strategies:
        - "NOTHING": No auto-tuning (use parameters exactly as specified)
        - "SCALING": Apply scaling_factor to model coefficients and parameters
        - "AUTO_SCALING": Automatically determine optimal scaling factor based on bit
        precision
        - "SAMPLING": Automatically determine temperature parameters through sampling
        - "AUTO_SCALING_AND_SAMPLING": Combine auto-scaling and sampling
        - "SCALING_AND_SAMPLING": Apply explicit scaling and determine temperatures
        Default is "NOTHING", giving full control to the user.
    scaling_factor: Union[int, float]
        Multiplicative factor applied to model coefficients, temperatures, and other
        parameters.
        Higher values can improve numerical precision but may lead to overflow.
        Default is 1.0 (no scaling).
    scaling_bit_precision: int
        Maximum bit precision to use when scaling. Determines the maximum allowable
        coefficient magnitude. Default is 64, using full double precision.
    guidance_config: Union[PartialConfig, None]
        Optional configuration for guiding the optimization process with prior
        knowledge. Can specify initial values or constraints for variables. Default is
        None.
    random_seed: Union[int, None]
        Seed for random number generation to ensure reproducible results.
        Must be between 0 and 9,999. Default is None (random seed).
    timeseries_max_bits: Union[int, None]
        Maximum number of bits to use for timeseries representation.
        Limits memory usage for large problems. Default is None (no limit).
    solver_max_bits: int
        Maximum problem size (in bits/variables) that the solver can handle.
        Default is 2¹³ (8,192), suitable for most solvers.
    var_shape_set: Optional[VarShapeSet]
        This parameter should be an object of :class:`VarShapeSet` or ``None``
    auto_fill_cold_bits: Optional[bool]
        In case ``var_shape_set`` is defined and contains a 1-hot group,
        and a hot bit is set to ``True`` and this parameter is also set to ``True``,
        then all related cold bits are set to ``False``. Default is ``True``
    """

    class BitArrayShape(BaseModel):
        """BitArrayShape.

        An object of the class :class:`BitArrayShape` represents an array structure as
        part of a bit vector. It allows multidimensional indexed access to the bit
        variables of a :class:`BinPol` polynomial. :class:`BitArrayShape` objects are
        used inside :class:`VarShapeSet` objects, which organize index data of a
        complete bit vector for a polynomial. Bit variables of such polynomials can
        then be accessed by name and indices according to the shape specified in the
        :class:`BitArrayShape` object.

        Parameters
        ----------
        shape: List[int]
            shape of the index; specify the length of each dimension
        constant_bits: Optional[NDArray]
            numpy array of type int8 with same shape as the previous parameter
            containing 0 and 1 for constant bits and -1 variable bits
        one_hot: OneHot
            define variable as one_hot section
        axis_names: Optional[List[str]]
            Names for the axis.
        index_offsets: Optional[List[int]]
            index_offsets of the index, specify the index_offsets of each dimension
        """

        type: Literal["BitArrayShape"] = "BitArrayShape"
        axis_names: list[str] | None = None
        index_offsets: list[int] | None = None
        name: str
        one_hot: Literal["no_way", "one_way", "two_way"] = "no_way"

    class Category(BaseModel):
        """Category.

        An object of the class :class:`Category` represents an array structure as part
        of a bit vector. It allows indexed access to the bit variables of a
        :class:`BinPol` polynomial. :class:`Category`
        objects are used inside :class:`VarShapeSet` objects, which organize index data
        of a complete bit vector for a polynomial. Bit variables of such polynomials
        can then be accessed by ``name`` and categorical indices according to the
        ``values`` specified in the :class:`BitArrayShape` object. A categorical index
        can be any sequence of unique values.

        Parameters
        ----------
        name: str
            name of the new index
        values: List[Any]
            list of unique values for this category
        one_hot: OneHot
            define variable as one_hot section
        axis_names: List[str]
            Names for the axis.
        """

        type: Literal["Category"] = "Category"
        values: list[Any] = Field(default_factory=list)
        axis_names: list[str] | None = None
        name: str
        one_hot: Literal["no_way", "one_way", "two_way"] = "no_way"

    class Variable(BaseModel):
        """Variable.

        A ``Variable`` is a binary polynomial, that represents a numerical value
        according to values of the underlying bits. The variable is defined by a value
        range and a specific representation scheme that is realized in respective
        inherited classes.

        Parameters
        ----------
        name: str
            name of the variable
        start: float
            first number in the list of values to be represented by the variable
        stop: float
            stop value for the list of numbers to be represented by the variable; stop
            is omitted
        step: float
            increment for the list of numbers to be represented by the variable
        shape: List[int]
            shape of the index; specify the length of each dimension
        constant_bits: Optional[NDArray]
            numpy array of type int8 with same shape as the previous parameter
            containing 0 and 1 for constant bits and -1 variable bits
        one_hot: OneHot
            define variable as one_hot section
        """

        type: Literal["Variable"] = "Variable"
        start: float
        stop: float
        step: float

        shape: list[int] | None = None
        constant_bits: list[int] | None = None

        name: str
        one_hot: Literal["no_way", "one_way", "two_way"] = "no_way"

    class VarShapeSet(BaseModel):
        """VarShapeSet.

        :class:`dadk.BinPol.VarShapeSet` defines an indexing structure for the bits of
        a BinPol polynomial. Plain BinPol polynomials are defined on a set of bits
        indexed by a ``range(N)`` for some integer ``N``. The ``VarShapeSet`` lays
        a sequence of disjoint named sections over this linear structure. Bits within a
        section can be addressed by the defined name. With a ``BitArrayShape`` a
        section can be defined as multidimensional array and single bits in the section
        can be addressed by an appropriate tuple of indices. With a ``Variable``
        definition the section represents a number encoded in certain bit schemes; in
        this case it is possible to retrieve the represented value instead of reading
        single bits.

        Parameters
        ----------
        var_defs: Union[BitArrayShape, Variable, Category]
            one or more section definitions of type :class:`BitArrayShape`,
            :class:`Variable` or :class:`Category`
        one_hot_groups: Optional[List[OneHotGroup]]
            optional list of special one_hot group definitions
        """

        var_defs: list[
            Annotated[
                FujitsuCommonParamsMixin.BitArrayShape
                | FujitsuCommonParamsMixin.Variable
                | FujitsuCommonParamsMixin.Category,
                Field(discriminator="type"),
            ]
        ] = Field(default_factory=list)
        one_hot_groups: list[Literal["no_way", "one_way", "two_way"]] | None = None

    class PartialConfig:
        """Produces a dict that can be used for the annealing algorithm.

        The start state for an annealing or parallel tempering model can be specified.
        The used dictionary addresses bits with their flattened index. With the class
        :class:`PartialConfig` those bits can be specified on the symbolic level of
        :class:`BitArrayShape` or :class:`Variable` and the offsets in a
        :class:`VarShapeSet` are calculated automatically. Flat indices can be used
        directly, if they are known. For variables, indices are used directly and do
        not need to be adjusted by a global index consideration from the
        :class:`VarShapeSet`. After setting the start state accordingly, a string can
        be created with the method ``as_json``. If one_hot or two_hot specifications
        are given in :class:`VarShapeSet`, the dictionary generated in the methods
        ``get_dict`` or ``as_json`` is build up with respect to the set bit variables
        and one-way or two-way rules.

        The object is initialized by a :class:`VarShapeSet` object or None.
        An initialization with None can be used for :class:`BinPol`.

        Parameters
        ----------
        var_shape_set: Optional[VarShapeSet]
            This parameter should be an object of :class:`VarShapeSet` or ``None``
        auto_fill_cold_bits: bool
            In case ``var_shape_set`` is defined and contains a 1-hot group,
            and a hot bit is set to ``True`` and this parameter is also set to ``True``,
            then all related cold bits are set to ``False``. Default is ``True``
        """

        var_shape_set: FujitsuCommonParamsMixin.VarShapeSet | None = None
        auto_fill_cold_bits: bool = True

    auto_tuning: Literal[
        "NOTHING",
        "SCALING",
        "AUTO_SCALING",
        "SAMPLING",
        "AUTO_SCALING_AND_SAMPLING",
        "SCALING_AND_SAMPLING",
    ] = "NOTHING"
    scaling_factor: int | float = 1.0
    scaling_bit_precision: int = 64
    random_seed: int | None = Field(default=None, ge=0, le=9_999)
    timeseries_max_bits: int | None = None
    solver_max_bits: int = 2**13
    var_shape_set: VarShapeSet | None = None
    auto_fill_cold_bits: bool | None = True

from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self

from pipelex.core.pipes.pipe_run_params import BatchParams, make_output_multiplicity
from pipelex.exceptions import PipeDefinitionError
from pipelex.pipe_controllers.sub_pipe import SubPipe
from pipelex.tools.typing.validation_utils import has_more_than_one_among_attributes_from_list


class SubPipeBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pipe: str
    result: Optional[str] = None
    nb_output: Optional[int] = None
    multiple_output: Optional[bool] = None
    batch_over: Union[bool, str] = False
    batch_as: Optional[str] = None

    @model_validator(mode="after")
    def validate_multiple_output(self) -> Self:
        if has_more_than_one_among_attributes_from_list(self, attributes_list=["nb_output", "multiple_output"]):
            raise PipeDefinitionError("PipeStepBlueprint should have no more than '1' of nb_output or multiple_output")
        return self

    @model_validator(mode="after")
    def validate_batch_params(self) -> Self:
        batch_over_is_specified = self.batch_over is not False and self.batch_over != ""
        batch_as_is_specified = self.batch_as is not None and self.batch_as != ""

        if batch_over_is_specified and not batch_as_is_specified:
            raise PipeDefinitionError(f"In pipe '{self.pipe}': When 'batch_over' is specified, 'batch_as' must also be provided")

        if batch_as_is_specified and not batch_over_is_specified:
            raise PipeDefinitionError(f"In pipe '{self.pipe}': When 'batch_as' is specified, 'batch_over' must also be provided")

        return self

    def make_sub_pipe(self) -> SubPipe:
        output_multiplicity = make_output_multiplicity(
            nb_output=self.nb_output,
            multiple_output=self.multiple_output,
        )
        batch_params = BatchParams.make_optional_batch_params(
            input_list_name=self.batch_over,
            input_item_name=self.batch_as,
        )
        return SubPipe(
            pipe_code=self.pipe,
            output_name=self.result,
            output_multiplicity=output_multiplicity,
            batch_params=batch_params,
        )

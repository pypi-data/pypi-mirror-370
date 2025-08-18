from collections import UserDict, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from sigma.processing.pipeline import ProcessingItemBase


@dataclass
class ProcessingItemTrackingMixin:
    """
    Provides attributes and methods for tracking processing items applied to Sigma rule objects
    like detection items and conditions.
    """

    applied_processing_items: Set[str] = field(init=False, compare=False, default_factory=set)

    def add_applied_processing_item(self, processing_item: Optional["ProcessingItemBase"]) -> None:
        """Add identifier of processing item to set of applied processing items."""
        if processing_item is not None and processing_item.identifier is not None:
            self.applied_processing_items.add(processing_item.identifier)

    def was_processed_by(self, processing_item_id: str) -> bool:
        """Determines if detection item was processed by a processing item with the given id."""
        return processing_item_id in self.applied_processing_items


class FieldMappingTracking(UserDict[Optional[str], Set[str]]):
    """
    Tracking class for field mappings. Tracks initial field name to finally mapped name after a
    processing pipeline was applied. Each key maps the source field to a set of target fields.

    Currently this class is intentionally only used to track field mappings in detection items and
    the fields list is excluded from it. This might change in the future depending on use cases.
    """

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.target_fields: defaultdict[Optional[str], Set[Optional[str]]] = defaultdict(
            set
        )  # Create reverse mapping

    def add_mapping(self, source: Optional[str], target: Union[str, List[str]]) -> None:
        """
        This method must be invoked for each field name mapping applied in a processing pipeline to
        get a precise result of the final mapping.
        """
        if not isinstance(target, list):  # Ensure that the target is a list.
            target = [target]

        if source in self.target_fields:  # Source field was already mapping target.
            # Replace each occurrence of a mapping to the source with the target field.
            for source_field in self.target_fields[source]:
                target_set = self[source_field]
                if source is not None:
                    target_set.remove(source)
                target_set.update(target)

            # Update reverse mapping: remove source and add new target
            del self.target_fields[source]
            for t in target:
                self.target_fields[t].add(source_field)

        if source not in self:
            self[source] = set(target)
        else:
            self[source].update(target)
        for t in target:
            self.target_fields[t].add(source)

    def merge(self, other: "FieldMappingTracking") -> None:
        """Merge another FieldMappingTracking into this one."""
        for source, target_set in other.items():
            self.add_mapping(source, list(target_set))

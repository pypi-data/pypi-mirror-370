import logging

from django.core.exceptions import ValidationError

from django_bulk_hooks.registry import get_hooks

logger = logging.getLogger(__name__)


def run(model_cls, event, new_records, old_records=None, ctx=None):
    """
    Run hooks for a given model, event, and records.
    """
    if not new_records:
        return

    # Get hooks for this model and event
    hooks = get_hooks(model_cls, event)

    if not hooks:
        return

    import traceback

    stack = traceback.format_stack()
    print(
        f"DEBUG: engine.run called for {model_cls.__name__}.{event} with {len(new_records)} records"
    )
    print(f"DEBUG: Call stack (last 3 frames):")
    for line in stack[-4:-1]:  # Show last 3 frames before this one
        print(f"  {line.strip()}")

    # For BEFORE_* events, run model.clean() first for validation
    if event.startswith("before_"):
        for instance in new_records:
            try:
                instance.clean()
            except ValidationError as e:
                logger.error("Validation failed for %s: %s", instance, e)
                raise

    # Process hooks
    for handler_cls, method_name, condition, priority in hooks:
        handler_instance = handler_cls()
        func = getattr(handler_instance, method_name)

        to_process_new = []
        to_process_old = []

        for new, original in zip(
            new_records,
            old_records or [None] * len(new_records),
            strict=True,
        ):
            if not condition or condition.check(new, original):
                to_process_new.append(new)
                to_process_old.append(original)

        if to_process_new:
            print(
                f"DEBUG: Executing hook {handler_cls.__name__}.{method_name} for {len(to_process_new)} records"
            )
            try:
                func(
                    new_records=to_process_new,
                    old_records=to_process_old if any(to_process_old) else None,
                )
            except Exception as e:
                raise

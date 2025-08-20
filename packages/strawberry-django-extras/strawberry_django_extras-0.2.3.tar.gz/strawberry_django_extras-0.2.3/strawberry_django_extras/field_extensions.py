from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable

import strawberry_django
from asgiref.sync import sync_to_async
from strawberry.extensions import FieldExtension
from strawberry_django.optimizer import DjangoOptimizerExtension

from .decorators import is_async, sync_or_async
from .functions import check_permissions, kill_a_rabbit, perform_validation, rabbit_hole
from .inputs import CRUDInput
from .types import PaginatedList

if TYPE_CHECKING:
    from strawberry.types import Info
    from strawberry_django.fields.base import StrawberryDjangoFieldBase
    from strawberry_django.fields.field import StrawberryDjangoField


# noinspection PyUnresolvedReferences,PyPropertyAccess
class MutationHooks(FieldExtension):
    argument_name: str

    # noinspection PyUnresolvedReferences
    def __init__(
        self,
        pre: Callable | None = None,
        post: Callable | None = None,
        pre_async: Callable | None = None,
        post_async: Callable | None = None,
    ):
        self.pre = pre
        self.post = post
        self.pre_async = pre_async
        self.post_async = post_async

    def apply(self, field: StrawberryDjangoField) -> None:
        if is_async():
            field.is_async = True
        self.argument_name = field.argument_name

    if not is_async():

        def resolve(self, next_, source, info, **kwargs):
            if self.pre:
                self.pre(info, kwargs.get(self.argument_name, None))

            result = next_(source, info, **kwargs)

            if self.post:
                self.post(info, kwargs.get(self.argument_name, None), result)
            return result

    else:

        async def resolve_async(
            self,
            next_: Callable[..., Awaitable[Any]],
            source: Any,
            info: Info,
            **kwargs: Any,
        ) -> Any:
            if self.pre_async:
                await self.pre_async(info, kwargs.get(self.argument_name, None))
            elif self.pre:
                await sync_or_async(self.pre)(info, kwargs.get(self.argument_name, None))

            result = await next_(source, info, **kwargs)

            if self.post_async:
                await self.post_async(info, kwargs.get(self.argument_name, None), result)
            elif self.post:
                await sync_or_async(self.post)(info, kwargs.get(self.argument_name, None), result)

            return result


# noinspection PyPropertyAccess
class Validators(FieldExtension):
    argument_name: str

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

    def apply(self, field: StrawberryDjangoField) -> None:
        if is_async():
            field.is_async = True
        self.argument_name = field.argument_name

    if not is_async():

        def resolve(self, next_, source, info, **kwargs):
            mutation_input = kwargs.get(self.argument_name, None)
            perform_validation(mutation_input, info)
            return next_(source, info, **kwargs)

    else:

        async def resolve_async(
            self,
            next_: Callable[..., Awaitable[Any]],
            source: Any,
            info: Info,
            **kwargs: Any,
        ) -> Any:
            mutation_input = kwargs.get(self.argument_name, None)
            await sync_to_async(perform_validation)(mutation_input, info)
            return await next_(source, info, **kwargs)


# noinspection PyPropertyAccess
class Permissions(FieldExtension):
    argument_name: str

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

    def apply(self, field: StrawberryDjangoField) -> None:
        if is_async():
            field.is_async = True
        self.argument_name = field.argument_name

    if not is_async():

        def resolve(self, next_, source, info, **kwargs):
            mutation_input = kwargs.get(self.argument_name, None)
            check_permissions(mutation_input, info)
            return next_(source, info, **kwargs)

    else:

        async def resolve_async(
            self,
            next_: Callable[..., Awaitable[Any]],
            source: Any,
            info: Info,
            **kwargs: Any,
        ) -> Any:
            mutation_input = kwargs.get(self.argument_name, None)
            await sync_to_async(check_permissions)(mutation_input, info)
            return await next_(source, info, **kwargs)


# noinspection PyPropertyAccess
class Relationships(FieldExtension):
    root_field: StrawberryDjangoFieldBase = None
    argument_name: str

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

    def apply(self, field: StrawberryDjangoField) -> None:
        self.root_field = field
        if is_async():
            field.is_async = True
        self.argument_name = field.argument_name

    if not is_async():

        def resolve(self, next_, source, info, **kwargs):
            mutation_input = kwargs.get(self.argument_name, None)
            model = self.root_field.django_model
            rel = {}
            rabbit_hole(model, mutation_input, rel)
            for k, v in mutation_input.__dict__.copy().items():
                if isinstance(v, CRUDInput):
                    delattr(mutation_input, k)

            with DjangoOptimizerExtension.disabled():
                return kill_a_rabbit(
                    rel,
                    None,
                    False,
                    is_root=True,
                    next_=next_,
                    source=source,
                    info=info,
                    ni=mutation_input,
                    argument_name=self.argument_name,
                )

    else:
        # noinspection PyArgumentList
        async def resolve_async(
            self,
            next_: Callable[..., Awaitable[Any]],
            source: Any,
            info: Info,
            **kwargs: Any,
        ) -> Any:
            mutation_input = kwargs.get(self.argument_name, None)
            model = self.root_field.django_model
            rel = {}
            await sync_to_async(rabbit_hole)(model, mutation_input, rel, None)
            for k, v in mutation_input.__dict__.copy().items():
                if isinstance(v, CRUDInput):
                    delattr(mutation_input, k)

            with await sync_to_async(DjangoOptimizerExtension.disabled)():
                return await sync_to_async(kill_a_rabbit, thread_sensitive=False)(
                    rel,
                    None,
                    False,
                    is_root=True,
                    next_=next_,
                    source=source,
                    info=info,
                    ni=mutation_input,
                    default_argument_name=self.argument_name,
                )


# noinspection PyPropertyAccess
class TotalCountPaginationExtension(FieldExtension):
    django_model = None

    def apply(self, field: StrawberryDjangoField) -> None:
        # Resolve these now before changing the type
        field.is_list = field.is_list
        field.django_model = field.django_model
        field.django_type = field.django_type

        self.django_model = field.django_model

        # Now change the type
        field.type = PaginatedList[field.type]

        if is_async():
            field.is_async = True

    @sync_or_async
    def get_total_count(self, info: Info, filters=None) -> int:
        if filters is not None:
            return strawberry_django.filters.apply(
                filters,
                self.django_model.objects.all(),
                info,
            ).count()
        return self.django_model.objects.count()

    if not is_async():

        def resolve(self, next_, source, info, **kwargs):
            result = next_(source, info, **kwargs)
            return PaginatedList(
                results=result,
                total_count=self.get_total_count(
                    filters=kwargs.get("filters", None),
                    info=info,
                ),
            )

    else:

        async def resolve_async(
            self,
            next_: Callable[..., Awaitable[Any]],
            source: Any,
            info: Info,
            **kwargs: Any,
        ) -> Any:
            result = await next_(source, info, **kwargs)
            return PaginatedList(
                results=result,
                total_count=self.get_total_count(
                    filters=kwargs.get("filters", None),
                    info=info,
                ),
            )


# Factory functions for extensions
def mutation_hooks(
    pre: callable = None,  # noqa: RUF013
    post: callable = None,  # noqa: RUF013
    pre_async: callable = None,  # noqa: RUF013
    post_async: callable = None,  # noqa: RUF013
):
    """Create a MutationHooks extension with the specified hooks."""
    return MutationHooks(pre, post, pre_async, post_async)


def with_validation():
    """Create a Validators extension."""
    return Validators()


def with_permissions():
    """Create a Permissions extension."""
    return Permissions()


def with_cud_relationships():
    """Create a Relationships extension."""
    return Relationships()


def with_total_count():
    """Create a TotalCountPaginationExtension."""
    return TotalCountPaginationExtension()

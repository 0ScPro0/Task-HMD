from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import RequestService, UserService
from src.database import Request, RequestStatus, RequestType, User, UserRole
from schemas.request import RequestResponse  # type: ignore
from core.exceptions import NotFoundError, PermissionDeniedError  # type: ignore


# ============================================================
# TESTS: get_requests_by_user
# ============================================================


@pytest.mark.asyncio
async def test_get_requests_by_user_with_5_requests(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Пользователь получает свои заявки - у пользователя есть 5 заявок, limit=100
    Ожидать список из 5 RequestResponse с корректными полями
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234567",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Create 5 requests for this user
    for i in range(5):
        request_data = request_create_schema_factory(
            type=RequestType.ELECTRICIAN,
            title=f"Request {i}",
            description=f"Description {i}",
            owner_id=user.id,
        )
        await request_service.create_request(request_data)

    # Call service method
    result = await request_service.get_requests_by_user(user=user, limit=100)

    # Assertions
    assert len(result) == 5
    assert any(isinstance(req, RequestResponse) for req in result)
    for i, request in enumerate(result):
        assert request.title == f"Request {i}"
        assert request.description == f"Description {i}"
        assert request.owner_id == user.id
        assert request.type == RequestType.ELECTRICIAN
        assert request.status == RequestStatus.NEW


@pytest.mark.asyncio
async def test_get_requests_by_user_no_requests(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
):
    """
    Пользователь без заявок - у пользователя нет ни одной заявки в БД
    Ожидать NotFoundError с сообщением "User has not any requests"
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="owner2@example.com",
        name="Owner2",
        surname="Owner2",
        phone="+79991234568",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Expect NotFoundError
    with pytest.raises(NotFoundError):
        await request_service.get_requests_by_user(user=user, limit=100)


# ============================================================
# TESTS: get_new_requests_by_role
# ============================================================


@pytest.mark.asyncio
async def test_get_new_requests_by_role_electrician_with_3_new(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Электрик получает новые заявки - role=ELECTRICIAN, есть 3 NEW заявки для электрика
    Ожидать список из 3 заявок со статусом NEW
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234567",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create electrician
    electrician_data = user_create_schema_factory(
        email="executor@example.com",
        name="Electrician",
        surname="Electrician",
        phone="+79991234561",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    electrician = await user_service.create(electrician_data)

    # Create 3 NEW electrician requests
    for i in range(3):
        request_data = request_create_schema_factory(
            type=RequestType.ELECTRICIAN,
            title=f"Electrician Request {i}",
            description=f"Description {i}",
            owner_id=owner.id,
            status=RequestStatus.NEW,
        )
        await request_service.create_request(request_data)

    # Call service method
    result = await request_service.get_new_requests_by_executor_role(
        executor=electrician, limit=100
    )
    if not result:
        raise NotFoundError("Request not found")

    # Assertions
    assert len(result) == 3
    for resp in result:
        assert resp.type == RequestType.ELECTRICIAN
        assert resp.status == RequestStatus.NEW


@pytest.mark.asyncio
async def test_get_new_requests_by_role_plumber_with_2_new(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Сантехник получает новые заявки - role=PLUMBER, есть 2 NEW заявки для сантехника
    Ожидать список из 2 заявок типа PLUMBER
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner2@example.com",
        name="Owner2",
        surname="Owner2",
        phone="+79991234568",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create plumber
    plumber_data = user_create_schema_factory(
        email="executor@example.com",
        name="Plumber",
        surname="Plumber",
        phone="+79991234561",
        role=UserRole.PLUMBER,
        password_hash="very_secure_password",
    )
    plumber = await user_service.create(plumber_data)

    # Create 2 NEW plumber requests
    for i in range(2):
        request_data = request_create_schema_factory(
            type=RequestType.PLUMBER,
            title=f"Plumber Request {i}",
            description=f"Description {i}",
            owner_id=owner.id,
            status=RequestStatus.NEW,
        )
        await request_service.create_request(request_data)

    # Call service method
    result = await request_service.get_new_requests_by_executor_role(
        executor=plumber, limit=100
    )
    if not result:
        raise NotFoundError("Request not found")

    # Assertions
    assert len(result) == 2
    for resp in result:
        assert resp.type == RequestType.PLUMBER
        assert resp.status == RequestStatus.NEW


@pytest.mark.asyncio
async def test_get_new_requests_by_role_no_new_requests(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Нет новых заявок для роли - role=ELECTRICIAN, в БД нет NEW заявок для электрика
    Ожидать пустой список []
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner3@example.com",
        name="Owner3",
        surname="Owner3",
        phone="+79991234569",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create plumber
    plumber_data = user_create_schema_factory(
        email="executor@example.com",
        name="Plumber",
        surname="Plumber",
        phone="+79991234561",
        role=UserRole.PLUMBER,
        password_hash="very_secure_password",
    )
    plumber = await user_service.create(plumber_data)

    # Create a request with status IN_PROGRESS (not NEW)
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="In Progress Request",
        description="Description",
        owner_id=owner.id,
        status=RequestStatus.IN_PROGRESS,
    )
    await request_service.create_request(request_data)

    # Call service method
    result = await request_service.get_new_requests_by_executor_role(
        executor=plumber, limit=100
    )

    # Should return empty list
    assert result == []


# ============================================================
# TESTS: get_request
# ============================================================


@pytest.mark.asyncio
async def test_get_request_admin_can_get_any(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Админ получает любую заявку - пользователь с ролью ADMIN, request_id=5
    Ожидать RequestResponse с правильным id=5
    """
    # Create admin user
    admin_data = user_create_schema_factory(
        email="admin@example.com",
        name="Admin",
        surname="Admin",
        phone="+79991234570",
        role=UserRole.ADMIN,
        password_hash="very_secure_password",
    )
    admin = await user_service.create(admin_data)

    # Create a request owned by another user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234571",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Test Request",
        description="Test Description",
        owner_id=owner.id,
    )
    request = await request_service.create_request(request_data)

    # Admin should be able to get the request
    result = await request_service.get_request(user=admin, request_id=request.id)

    assert isinstance(result, RequestResponse)
    assert result.id == request.id
    assert result.title == request.title
    assert result.owner_id == owner.id


@pytest.mark.asyncio
async def test_get_request_owner_can_get_own(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Владелец получает свою заявку - user.id == request.owner_id, request_id существующий
    Ожидать RequestResponse с доступом к заявке
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234572",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Owner Request",
        description="Owner Description",
        owner_id=owner.id,
    )
    request = await request_service.create_request(request_data)

    # Owner should be able to get the request
    result = await request_service.get_request(user=owner, request_id=request.id)

    assert isinstance(result, RequestResponse)
    assert result.id == request.id
    assert result.owner_id == owner.id


@pytest.mark.asyncio
async def test_get_request_executor_can_get_assigned(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Исполнитель получает заявку - user.id == request.executor_id, заявка назначена на него
    Ожидать RequestResponse с корректными данными
    """
    # Create executor user (electrician)
    executor_data = user_create_schema_factory(
        email="executor@example.com",
        name="Executor",
        surname="Executor",
        phone="+79991234573",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    executor = await user_service.create(executor_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234574",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request assigned to executor
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Assigned Request",
        description="Assigned Description",
        owner_id=owner.id,
        executor_id=executor.id,
        status=RequestStatus.IN_PROGRESS,
    )
    request = await request_service.create_request(request_data)
    print(request)

    # Executor should be able to get the request
    result = await request_service.get_request(user=executor, request_id=request.id)

    assert isinstance(result, RequestResponse)
    assert result.id == request.id
    assert result.executor_id == executor.id


@pytest.mark.asyncio
async def test_get_request_foreign_user_permission_denied(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Чужой пользователь получает заявку - не админ, не владелец, не исполнитель
    Ожидать PermissionDeniedError "Only admin, owner or executor can get request"
    """
    # Create foreign user
    foreign_data = user_create_schema_factory(
        email="foreign@example.com",
        name="Foreign",
        surname="Foreign",
        phone="+79991234575",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    foreign = await user_service.create(foreign_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234576",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request owned by owner, not assigned to foreign
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Foreign Request",
        description="Foreign Description",
        owner_id=owner.id,
    )
    request = await request_service.create_request(request_data)

    # Foreign user should be denied
    with pytest.raises(PermissionDeniedError):
        await request_service.get_request(user=foreign, request_id=request.id)


@pytest.mark.asyncio
async def test_get_request_not_found(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
):
    """
    Заявка не найдена - передан несуществующий request_id=999
    Ожидать NotFoundError с сообщением "Request not found"
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="user@example.com",
        name="User",
        surname="User",
        phone="+79991234577",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Non-existent request ID
    with pytest.raises(NotFoundError):
        await request_service.get_request(user=user, request_id=999)


# ============================================================
# TESTS: delete_request
# ============================================================


@pytest.mark.asyncio
async def test_delete_request_admin_can_delete(
    request_service: RequestService,
    user_service: UserService,
    test_session: AsyncSession,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Админ удаляет заявку - user_role=ADMIN, request_id=5 существует
    Ожидать возврат True, заявка исчезает из БД
    """
    # Create admin user
    admin_data = user_create_schema_factory(
        email="admin@example.com",
        name="Admin",
        surname="Admin",
        phone="+79991234599",
        role=UserRole.ADMIN,
        password_hash="very_secure_password",
    )
    admin = await user_service.create(admin_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234600",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Request to Delete",
        description="Description",
        owner_id=owner.id,
    )
    request = await request_service.create_request(request_data)

    # Admin deletes the request
    result = await request_service.delete_request(
        user=admin,
        request_id=request.id,
    )

    assert result is True

    # Verify request is deleted
    deleted = await test_session.get(Request, request.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_request_owner_can_delete_own(
    request_service: RequestService,
    user_service: UserService,
    test_session: AsyncSession,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Владелец удаляет свою заявку - request.owner_id == user_id, request_id существует
    Ожидать True и удаление заявки
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234601",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request owned by owner
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Owner Request",
        description="Owner Description",
        owner_id=owner.id,
    )
    request = await request_service.create_request(request_data)

    # Owner deletes the request
    result = await request_service.delete_request(
        user=owner,
        request_id=request.id,
    )

    assert result is True

    # Verify request is deleted
    deleted = await test_session.get(Request, request.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_request_executor_can_delete(
    request_service: RequestService,
    user_service: UserService,
    test_session: AsyncSession,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Исполнитель удаляет заявку - request.executor_id == user_id, request_id существует
    Ожидать True и успешное удаление
    """
    # Create executor user
    executor_data = user_create_schema_factory(
        email="executor@example.com",
        name="Executor",
        surname="Executor",
        phone="+79991234602",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    executor = await user_service.create(executor_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234603",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request assigned to executor
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Executor Request",
        description="Executor Description",
        owner_id=owner.id,
        executor_id=executor.id,
        status=RequestStatus.IN_PROGRESS,
    )
    request = await request_service.create_request(request_data)

    # Executor deletes the request
    result = await request_service.delete_request(
        user=executor,
        request_id=request.id,
    )

    assert result is True

    # Verify request is deleted
    deleted = await test_session.get(Request, request.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_request_foreign_user_permission_denied(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Чужой пользователь удаляет заявку - не админ, не владелец, не исполнитель
    Ожидать PermissionDeniedError "Only admin, worker or request owner can delete request"
    """
    # Create foreign user
    foreign_data = user_create_schema_factory(
        email="foreign@example.com",
        name="Foreign",
        surname="Foreign",
        phone="+79991234604",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    foreign = await user_service.create(foreign_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234605",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request owned by owner, not assigned to foreign
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Foreign Request",
        description="Foreign Description",
        owner_id=owner.id,
    )
    request = await request_service.create_request(request_data)

    # Foreign user tries to delete
    with pytest.raises(PermissionDeniedError):
        await request_service.delete_request(
            user=foreign,
            request_id=request.id,
        )


@pytest.mark.asyncio
async def test_delete_request_not_found(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
):
    """
    Заявка не найдена - передан несуществующий request_id=999 при удалении
    Ожидать NotFoundError "Request not found"
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="user@example.com",
        name="User",
        surname="User",
        phone="+79991234606",
        role=UserRole.ADMIN,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Non-existent request ID
    with pytest.raises(NotFoundError):
        await request_service.delete_request(
            user=user,
            request_id=999,
        )


# ============================================================
# PERFORMANCE TEST: huge limit in get_requests_by_user
# ============================================================


@pytest.mark.asyncio
async def test_get_requests_by_user_huge_limit(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Огромный limit в get_requests_by_user - передать limit=1000000, хотя у пользователя только 10000 заявок
    проверить, что метод не падает и возвращает все заявки пользователя
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="perfuser@example.com",
        name="PerfUser",
        surname="PerfUser",
        phone="+79991234607",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Create 100 requests for this user (simulating many requests)
    # In a real performance test you might create 10000, but for unit test we keep it small
    for i in range(100):
        request_data = request_create_schema_factory(
            type=RequestType.ELECTRICIAN,
            title=f"Request {i}",
            description=f"Description {i}",
            owner_id=user.id,
        )
        await request_service.create_request(request_data)

    # Call service method with huge limit
    result = await request_service.get_requests_by_user(user=user, limit=1_000_000)

    # Should return all 100 requests
    assert len(result) == 100
    assert all(isinstance(item, RequestResponse) for item in result)
    # Ensure all belong to the user
    for resp in result:
        assert resp.owner_id == user.id


# ============================================================
# TESTS: update_request_status
# ============================================================


@pytest.mark.asyncio
async def test_update_request_status_admin_can_change_any(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Админ меняет статус любой заявки - user_role=ADMIN, request_id=5, status=COMPLETED
    Ожидать обновленный RequestResponse со статусом COMPLETED
    """
    # Create admin user (we only need user_id and role)
    admin_data = user_create_schema_factory(
        email="admin@example.com",
        name="Admin",
        surname="Admin",
        phone="+79991234592",
        role=UserRole.ADMIN,
        password_hash="very_secure_password",
    )
    admin = await user_service.create(admin_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234593",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Request to Complete",
        description="Description",
        owner_id=owner.id,
        status=RequestStatus.IN_PROGRESS,
    )
    request = await request_service.create_request(request_data)

    # Admin changes status to COMPLETED
    result = await request_service.update_request_status(
        user=admin,
        request_id=request.id,
        status=RequestStatus.COMPLETED,
    )

    assert result.status == RequestStatus.COMPLETED
    assert result.id == request.id


@pytest.mark.asyncio
async def test_update_request_status_executor_can_change_own(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Исполнитель меняет статус своей заявки - request.executor_id == user_id, status=IN_PROGRESS
    Ожидать обновленный статус в ответе
    """
    # Create executor user
    executor_data = user_create_schema_factory(
        email="executor@example.com",
        name="Executor",
        surname="Executor",
        phone="+79991234594",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    executor = await user_service.create(executor_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234595",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request assigned to executor
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Executor Request",
        description="Executor Description",
        owner_id=owner.id,
        executor_id=executor.id,
        status=RequestStatus.IN_PROGRESS,
    )
    request = await request_service.create_request(request_data)

    # Executor changes status to COMPLETED
    result = await request_service.update_request_status(
        user=executor,
        request_id=request.id,
        status=RequestStatus.COMPLETED.value,
    )

    assert result.status == RequestStatus.COMPLETED
    assert result.executor_id == executor.id


@pytest.mark.asyncio
async def test_update_request_status_non_admin_non_executor_permission_denied(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Не-админ и не-исполнитель меняет статус - обычный пользователь пытается изменить статус чужой заявки
    Ожидать PermissionDeniedError
    """
    # Create foreign user
    foreign_data = user_create_schema_factory(
        email="foreign@example.com",
        name="Foreign",
        surname="Foreign",
        phone="+79991234596",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    foreign = await user_service.create(foreign_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234597",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create a request owned by owner, not assigned to foreign
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Foreign Request",
        description="Foreign Description",
        owner_id=owner.id,
        status=RequestStatus.NEW,
    )
    request = await request_service.create_request(request_data)

    # Foreign user tries to change status
    with pytest.raises(PermissionDeniedError):
        await request_service.update_request_status(
            user=foreign,
            request_id=request.id,
            status=RequestStatus.COMPLETED,
        )


@pytest.mark.asyncio
async def test_update_request_status_not_found(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
):
    """
    Заявка не найдена - передан несуществующий request_id=999 при смене статуса
    Ожидать NotFoundError "Request not found"
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="user@example.com",
        name="User",
        surname="User",
        phone="+79991234598",
        role=UserRole.ADMIN,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Non-existent request ID
    with pytest.raises(NotFoundError):
        await request_service.update_request_status(
            user=user, request_id=999, status=RequestStatus.COMPLETED
        )


# ============================================================
# TESTS: create_request
# ============================================================


@pytest.mark.asyncio
async def test_create_request_with_valid_data(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Создание заявки с корректными данными - передать валидный RequestCreate с типом и описанием
    Ожидать созданный объект Request с присвоенным id
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234578",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create RequestCreate schema
    request_create = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="New Request",
        description="New Description",
        owner_id=owner.id,
    )

    # Call service method
    created_request = await request_service.create_request(request=request_create)

    # Assertions
    assert created_request is not None
    assert created_request.id is not None
    assert created_request.title == "New Request"
    assert created_request.description == "New Description"
    assert created_request.type == RequestType.ELECTRICIAN
    assert created_request.owner_id == owner.id
    assert created_request.status == RequestStatus.NEW


# ============================================================
# TESTS: executor_accept_request
# ============================================================


@pytest.mark.asyncio
async def test_executor_accept_request_electrician_new(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Электрик принимает NEW заявку электрика - request.type=ELECTRICIAN, status=NEW, user.role=ELECTRICIAN
    Ожидать статус IN_PROGRESS и заполненный executor_id
    """
    # Create electrician user (executor)
    electrician_data = user_create_schema_factory(
        email="electrician@example.com",
        name="Electrician",
        surname="Electrician",
        phone="+79991234579",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    electrician = await user_service.create(electrician_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234580",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create NEW electrician request
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Electrician Request",
        description="Electrician Description",
        owner_id=owner.id,
        status=RequestStatus.NEW,
    )
    request = await request_service.create_request(request_data)

    # Electrician accepts the request
    result = await request_service.executor_accept_request(
        request_id=request.id,
        executor=electrician,
    )

    # Assertions
    assert result.status == RequestStatus.IN_PROGRESS
    assert result.executor_id == electrician.id


@pytest.mark.asyncio
async def test_executor_accept_request_plumber_new(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Сантехник принимает NEW заявку сантехника - request.type=PLUMBER, status=NEW, user.role=PLUMBER
    Ожидать статус IN_PROGRESS и executor_id=user.id
    """
    # Create plumber user (executor)
    plumber_data = user_create_schema_factory(
        email="plumber@example.com",
        name="Plumber",
        surname="Plumber",
        phone="+79991234581",
        role=UserRole.PLUMBER,
        password_hash="very_secure_password",
    )
    plumber = await user_service.create(plumber_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234582",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create NEW plumber request
    request_data = request_create_schema_factory(
        type=RequestType.PLUMBER,
        title="Plumber Request",
        description="Plumber Description",
        owner_id=owner.id,
        status=RequestStatus.NEW,
    )
    request = await request_service.create_request(request_data)

    # Plumber accepts the request
    result = await request_service.executor_accept_request(
        request_id=request.id,
        executor=plumber,
    )

    # Assertions
    assert result.status == RequestStatus.IN_PROGRESS
    assert result.executor_id == plumber.id


@pytest.mark.asyncio
async def test_executor_accept_request_admin_new(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Админ принимает любую NEW заявку - user.role=ADMIN, request.status=NEW
    Ожидать статус IN_PROGRESS, executor_id установлен
    """
    # Create admin user
    admin_data = user_create_schema_factory(
        email="admin@example.com",
        name="Admin",
        surname="Admin",
        phone="+79991234583",
        role=UserRole.ADMIN,
        password_hash="very_secure_password",
    )
    admin = await user_service.create(admin_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234584",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create NEW electrician request
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Admin Accept Request",
        description="Admin Accept Description",
        owner_id=owner.id,
        status=RequestStatus.NEW,
    )
    request = await request_service.create_request(request_data)

    # Admin accepts the request (assigns to themselves)
    result = await request_service.executor_accept_request(
        request_id=request.id,
        executor=admin,
    )

    # Assertions
    assert result.status == RequestStatus.IN_PROGRESS
    assert result.executor_id == admin.id


@pytest.mark.asyncio
async def test_executor_accept_request_in_progress_update_executor(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Принятие уже IN_PROGRESS заявки - request.status=IN_PROGRESS, другой исполнитель принимает
    Ожидать PermissionDeniedError
    """
    # Create first executor
    executor1_data = user_create_schema_factory(
        email="executor1@example.com",
        name="Executor1",
        surname="Executor1",
        phone="+79991234585",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    executor1 = await user_service.create(executor1_data)

    # Create second executor
    executor2_data = user_create_schema_factory(
        email="executor2@example.com",
        name="Executor2",
        surname="Executor2",
        phone="+79991234586",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    executor2 = await user_service.create(executor2_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234587",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create IN_PROGRESS request assigned to executor1
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="In Progress Request",
        description="In Progress Description",
        owner_id=owner.id,
        executor_id=executor1.id,
        status=RequestStatus.IN_PROGRESS,
    )
    request = await request_service.create_request(request_data)

    # Executor2 accepts the request (reassigns)
    with pytest.raises(PermissionDeniedError):
        await request_service.executor_accept_request(
            request_id=request.id,
            executor=executor2,
        )


@pytest.mark.asyncio
async def test_executor_accept_request_wrong_role_permission_denied(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Исполнитель принимает заявку не своей роли - user.role=PLUMBER, но request.type=ELECTRICIAN
    Ожидать PermissionDeniedError "Only admin or executer with same role"
    """
    # Create plumber user
    plumber_data = user_create_schema_factory(
        email="plumber@example.com",
        name="Plumber",
        surname="Plumber",
        phone="+79991234588",
        role=UserRole.PLUMBER,
        password_hash="very_secure_password",
    )
    plumber = await user_service.create(plumber_data)

    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234589",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create NEW electrician request
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Electrician Request",
        description="Electrician Description",
        owner_id=owner.id,
        status=RequestStatus.NEW,
    )
    request = await request_service.create_request(request_data)

    # Plumber tries to accept electrician request
    with pytest.raises(PermissionDeniedError):
        await request_service.executor_accept_request(
            request_id=request.id,
            executor=plumber,
        )


@pytest.mark.asyncio
async def test_executor_accept_request_owner_cannot_accept_own(
    request_service: RequestService,
    user_service: UserService,
    test_session: AsyncSession,
    user_create_schema_factory,
    request_create_schema_factory,
):
    """
    Пользователь принимает свою заявку - user.id == request.owner_id, пытается стать исполнителем
    Ожидать PermissionDeniedError "Can not respond to your own requests"
    """
    # Create owner user
    owner_data = user_create_schema_factory(
        email="owner@example.com",
        name="Owner",
        surname="Owner",
        phone="+79991234590",
        role=UserRole.RESIDENT,
        password_hash="very_secure_password",
    )
    owner = await user_service.create(owner_data)

    # Create NEW request owned by owner
    request_data = request_create_schema_factory(
        type=RequestType.ELECTRICIAN,
        title="Own Request",
        description="Own Description",
        owner_id=owner.id,
        status=RequestStatus.NEW,
    )
    request = await request_service.create_request(request_data)

    # Owner tries to accept own request
    with pytest.raises(PermissionDeniedError):
        await request_service.executor_accept_request(
            request_id=request.id,
            executor=owner,
        )


@pytest.mark.asyncio
async def test_executor_accept_request_not_found(
    request_service: RequestService,
    user_service: UserService,
    user_create_schema_factory,
):
    """
    Заявка не найдена - передан несуществующий request_id=999
    Ожидать NotFoundError "Request not found"
    """
    # Create a user
    user_data = user_create_schema_factory(
        email="user@example.com",
        name="User",
        surname="User",
        phone="+79991234591",
        role=UserRole.ELECTRICIAN,
        password_hash="very_secure_password",
    )
    user = await user_service.create(user_data)

    # Non-existent request ID
    with pytest.raises(NotFoundError):
        await request_service.executor_accept_request(request_id=999, executor=user)

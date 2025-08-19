"""Tests for Standard Bots Python SDKs."""

import time

import pytest
from standardbots import StandardBotsRobot
from standardbots.auto_generated import models
from standardbots.auto_generated.apis import RobotKind
from standardbots.auto_generated.models import RobotControlMode, RobotControlModeEnum


class TestAuthenticationMiddleware:
    """Tests for authentication"""

    @pytest.mark.parametrize(
        ["robot_kind"], [(RobotKind.Live,), (RobotKind.Simulated,)]
    )
    def test_authentication_bad(
        self, robot_kind: RobotKind, api_url: StandardBotsRobot
    ) -> None:
        """Must be authenticated for endpoint (io state)"""
        client = StandardBotsRobot(
            url=api_url,
            token="invalid",
            robot_kind=robot_kind,
        )
        with client.connection():
            res = client.io.status.get_io_state()
        assert res.status == 401

    @pytest.mark.parametrize(
        ["robot_kind"], [(RobotKind.Live,), (RobotKind.Simulated,)]
    )
    def test_authentication_good(
        self, robot_kind: RobotKind, api_url: str, api_token: str
    ) -> None:
        """Must be authenticated for endpoint (io state)."""
        client = StandardBotsRobot(
            url=api_url,
            token=api_token,
            robot_kind=robot_kind,
        )
        with client.connection():
            res = client.io.status.get_io_state()

        assert res.ok()

    @pytest.mark.parametrize(
        ["robot_kind"], [(RobotKind.Live,), (RobotKind.Simulated,)]
    )
    def test_not_authentication_ok(self, robot_kind: RobotKind, api_url: str) -> None:
        """No authentication needed for endpoint (health)."""
        client = StandardBotsRobot(
            url=api_url,
            token="invalid",
            robot_kind=robot_kind,
        )
        with client.connection():
            res = client.status.health.get_health()
        ok_res = res.ok()

        assert isinstance(ok_res, models.StatusHealthResponse)
        assert ok_res.health == models.StatusHealthEnum.Ok


@pytest.mark.skip("Not implemented")
class TestPostEquipmentEndEffectorControl:
    """Tests: [POST] `/api/v1/equipment/end-effector/control`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetEquipmentEndEffectorConfiguration:
    """Tests: [GET] `/api/v1/equipment/end-effector/configuration`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


class TestGetEquipmentCustomSensors:
    """Tests: [GET] `/api/v1/equipment/custom/sensors`"""

    @pytest.mark.custom_sensors
    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live

        with client.connection():
            res_raw = client.sensors.get_sensors()
        assert not res_raw.isNotOk()
        res = res_raw.ok()

        assert isinstance(res.sensors, list)
        assert len(res.sensors) > 0

        sensor = res.sensors[0]
        assert sensor.name == 'sensor 1'
        assert sensor.kind == 'controlBoxIO'
        assert sensor.sensorValue == 'low'

    @pytest.mark.custom_sensors
    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        client = client_sim

        with client.connection():
            res_raw = client.sensors.get_sensors()
        assert not res_raw.isNotOk()
        res = res_raw.ok()

        assert isinstance(res.sensors, list)
        assert len(res.sensors) > 0

        sensor = res.sensors[0]
        assert sensor.name == 'sensor 1'
        assert sensor.kind == 'controlBoxIO'
        assert sensor.sensorValue == 'low'

class TestGetMovementBrakes:
    """Tests: [GET] `/api/v1/movement/brakes`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live

        with client.connection():
            res = client.movement.brakes.get_brakes_state()

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state is not None

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        client = client_sim

        with client.connection():
            res = client.movement.brakes.get_brakes_state()

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state is not None


class TestPostMovementBrakes:
    """Tests: [POST] `/api/v1/movement/brakes`

    NOTE Relies on "get brake state" API
    """

    def test_brake_live(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live

        # ######################################
        # Get initial brakes state
        # ######################################
        with client.connection():
            res = client.movement.brakes.get_brakes_state()

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state is not None
        is_braked_initial = data.state == models.BrakesStateEnum.Engaged

        new_state = (
            models.BrakesStateEnum.Disengaged
            if is_braked_initial
            else models.BrakesStateEnum.Engaged
        )

        body = models.BrakesState(state=new_state)

        with client.connection():
            res = client.movement.brakes.set_brakes_state(body)

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state == new_state

        # ######################################
        # Confirm new state via other means
        # ######################################
        with client.connection():
            res = client.movement.brakes.get_brakes_state()

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state == new_state

        # ######################################
        # Set brakes state back to original state
        # ######################################
        final_state = (
            models.BrakesStateEnum.Disengaged
            if not is_braked_initial
            else models.BrakesStateEnum.Engaged
        )
        body = models.BrakesState(state=final_state)

        with client.connection():
            res = client.movement.brakes.set_brakes_state(body)

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state == final_state

    def test_brake_twice(self, client_live: StandardBotsRobot) -> None:
        """Test (un)braking twice

        Use the `client.movement.brakes.brake()`/`client.movement.brakes.unbrake()` helper methods.
        """
        client = client_live

        # ###################################################
        # Brake
        # ###################################################
        for _ in range(2):
            with client.connection():
                res = client.movement.brakes.brake()

            assert not res.isNotOk()
            data = res.data
            assert isinstance(data, models.BrakesState)
            assert data.state == models.BrakesStateEnum.Engaged

        # ###################################################
        # Now unbrake
        # ###################################################

        for _ in range(2):
            with client.connection():
                res = client.movement.brakes.unbrake()

            assert not res.isNotOk()
            data = res.data
            assert isinstance(data, models.BrakesState)
            assert data.state == models.BrakesStateEnum.Disengaged

    def test_brakes_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode

        Can observe sim braking/unbraking separate from live robot.
        """
        client = client_sim

        # ######################################
        # Get initial brakes state
        # ######################################
        with client.connection():
            res = client.movement.brakes.get_brakes_state()

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state is not None
        is_braked_initial = data.state == models.BrakesStateEnum.Engaged

        new_state = (
            models.BrakesStateEnum.Disengaged
            if is_braked_initial
            else models.BrakesStateEnum.Engaged
        )

        body = models.BrakesState(state=new_state)

        with client.connection():
            res = client.movement.brakes.set_brakes_state(body)

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state == new_state

        # ######################################
        # Confirm new state via other means
        # ######################################
        with client.connection():
            res = client.movement.brakes.get_brakes_state()

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state == new_state

        # ######################################
        # Set brakes state back to original state
        # ######################################
        final_state = (
            models.BrakesStateEnum.Disengaged
            if not is_braked_initial
            else models.BrakesStateEnum.Engaged
        )
        body = models.BrakesState(state=final_state)

        with client.connection():
            res = client.movement.brakes.set_brakes_state(body)

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.BrakesState)
        assert data.state == final_state


class TestPostMovementBrakesEmergencyStop:
    """Tests: [POST] `/api/v1/movement/brakes/emergency-stop`

    NOTE Rely on working recover.get_status/recover to test this.
    """

    @pytest.mark.parametrize(
        ["n_estops"], [pytest.param(1, id="1 e-stop"), pytest.param(2, id="2 e-stops")]
    )
    def test_basic(self, n_estops: int, client_live: StandardBotsRobot) -> None:
        """Basic test

        n_estops: Triggers e-stops multiple times. Ensure that can run multiple times.

        This test can be flaky at times. Sometimes the status check will return 'Idle' instead of 'EStopTriggered'.
        """
        client = client_live

        # ######################################
        # Ensure not already in error state
        # ######################################
        with client.connection():
            res_status = client.recovery.recover.get_status()

        assert not res_status.isNotOk()
        data = res_status.data
        assert isinstance(data, models.FailureStateResponse)
        assert not data.failed

        # ######################################
        # Now test e-stop operation
        # ######################################

        for _ in range(n_estops):
            body = models.EngageEmergencyStopRequest(reason="To test it out.")

            with client.connection():
                res = client.movement.brakes.engage_emergency_stop(body)

            assert not res.isNotOk()
            assert res.data is None

            # ######################################
            # Ensure status
            # ######################################

            for _ in range(2):
                with client.connection():
                    res_status = client.recovery.recover.get_status()

                assert not res_status.isNotOk()
                data = res_status.data
                assert isinstance(data, models.FailureStateResponse)
                if data.failure is None or data.failure.kind == "Idle":
                    time.sleep(1)  # Appears to take a moment to update at times?
                    continue
                if data.failure.kind == "EStopTriggered":
                    assert data.failed
                    break
                assert data.failure.kind == "EStopTriggered"

        # ######################################
        # Recover from e-stop
        # ######################################

        with client.connection():
            res_status = client.recovery.recover.recover()

    def test_estop_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode

        Sim does not e-stop the bot.
        """
        client = client_sim
        body = models.EngageEmergencyStopRequest(reason="To test it out.")

        with client.connection():
            res = client.movement.brakes.engage_emergency_stop(body)

        assert not res.isNotOk()
        assert res.data is None

        # ######################################
        # Sim does not e-stop the bot. So no recovery state.
        # ######################################

        with client.connection():
            res_status = client.recovery.recover.get_status()

        assert not res_status.isNotOk()
        data = res_status.data
        assert isinstance(data, models.FailureStateResponse)
        assert not data.failed


@pytest.mark.skip("Not implemented")
class TestGetMovementPositionArm:
    """Tests: [GET] `/api/v1/movement/position/arm`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostMovementPositionArm:
    """Tests: [POST] `/api/v1/movement/position/arm`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetMovementROSState:
    """Tests: [GET] `/api/v1/movement/ros/state`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostMovementROSState:
    """Tests: [POST] `/api/v1/movement/ros/state`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostRecoveryRecover:
    """Tests: [POST] `/api/v1/recovery/recover`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetRecoveryStatus:
    """Tests: [GET] `/api/v1/recovery/status`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostFaultsUserFault:
    """Tests: [POST] `/api/v1/faults/user-fault`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetCameraStreamRGB:
    """Tests: [GET] `/api/v1/camera/stream/rgb`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostCameraSettings:
    """Tests: [POST] `/api/v1/camera/settings`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetCameraFrameRGB:
    """Tests: [GET] `/api/v1/camera/frame/rgb`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetCameraIntrinsicsRGB:
    """Tests: [GET] `/api/v1/camera/intrinsics/rgb`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetCameraStatus:
    """Tests: [GET] `/api/v1/camera/status`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


class TestGetRoutineEditorRoutines:
    """Tests: [GET] `/api/v1/routine-editor/routines`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live
        limit = 10
        offset = 0
        with client.connection():
            res = client.routine_editor.routines.list(limit=limit, offset=offset)

        assert not res.isNotOk()
        data = res.ok()

        assert isinstance(data, models.RoutinesPaginatedResponse)
        assert len(data.items) <= limit
        assert data.pagination.total == len(data.items)
        assert data.pagination.limit == limit
        assert data.pagination.offset == offset

    def test_pagination(self, client_live: StandardBotsRobot) -> None:
        """Pagination test"""
        client = client_live
        limit = 10
        offset = 0
        with client.connection():
            res = client.routine_editor.routines.list(limit=limit, offset=offset)

        assert not res.isNotOk()
        data = res.ok()

        assert isinstance(data, models.RoutinesPaginatedResponse)
        assert len(data.items) > 2, "Expected >2 routines (necessary for other tests)"

        # #################################
        # Lower limit
        # #################################
        limit = len(data.items) - 2
        offset = 0
        with client.connection():
            res = client.routine_editor.routines.list(limit=limit, offset=offset)

        assert not res.isNotOk()
        data = res.ok()
        assert isinstance(data, models.RoutinesPaginatedResponse)
        assert data.pagination.total == len(data.items)
        assert len(data.items) <= limit
        assert data.pagination.limit == limit
        assert data.pagination.offset == offset

        # #################################
        # Higher offset
        # #################################
        limit = 10
        offset = 1
        with client.connection():
            res = client.routine_editor.routines.list(limit=limit, offset=offset)

        assert not res.isNotOk()
        data2 = res.ok()
        assert data2.pagination.total == len(data2.items)
        assert len(data2.items) <= limit
        assert data2.pagination.limit == limit
        assert data2.pagination.offset == offset
        assert data.items[0].id not in set(r.id for r in data2.items), (
            "Offset not working"
        )

    @pytest.mark.parametrize(
        ["limit"],
        [
            (0,),
            (-1,),
        ],
    )
    def test_bad_limit(self, limit: int, client_live: StandardBotsRobot) -> None:
        """Bad limit test"""
        client = client_live
        offset = 0
        with client.connection():
            res_raw = client.routine_editor.routines.list(limit=limit, offset=offset)

        assert res_raw.isNotOk()
        assert res_raw.status == 400
        assert isinstance(res_raw.data, models.ErrorResponse)
        assert res_raw.data.error == models.ErrorEnum.InvalidParameters
        assert res_raw.data.message == "Limit must be greater than 0."

    @pytest.mark.parametrize(
        ["offset"],
        [
            (-100,),
            (-1,),
        ],
    )
    def test_bad_offset(self, offset: int, client_live: StandardBotsRobot) -> None:
        """Bad limit test"""
        client = client_live
        limit = 10
        with client.connection():
            res_raw = client.routine_editor.routines.list(limit=limit, offset=offset)

        assert res_raw.isNotOk()
        assert res_raw.status == 400
        assert isinstance(res_raw.data, models.ErrorResponse)
        assert res_raw.data.error == models.ErrorEnum.InvalidParameters
        assert res_raw.data.message == "Offset must be greater than or equal to 0."


class TestGetRoutineEditorRoutineById:
    """Tests: [GET] `/api/v1/routine-editor/routines/:routineId`"""

    def test_basic(
        self, client_live: StandardBotsRobot, routine_sample: models.Routine
    ) -> None:
        """Basic test"""
        client = client_live
        routine_id = routine_sample.id
        with client.connection():
            res_raw = client.routine_editor.routines.load(routine_id=routine_id)

        assert not res_raw.isNotOk()
        assert res_raw.status == 200
        data = res_raw.ok()
        assert isinstance(data, models.Routine)
        assert data.id == routine_id
        assert data.name == routine_sample.name

        assert len(data.environment_variables) > 0
        assert any(
            ev.name == "my_local_variable" for ev in data.environment_variables
        ), "Failed to find expected environment variable"

    def test_invalid_id(self, client_live: StandardBotsRobot) -> None:
        """Invalid ID returns 404"""
        client = client_live
        routine_id = "invalid"
        with client.connection():
            res_raw = client.routine_editor.routines.load(routine_id=routine_id)

        assert res_raw.isNotOk()
        assert res_raw.status == 404
        assert isinstance(res_raw.data, models.ErrorResponse)
        assert res_raw.data.error == models.ErrorEnum.NotFound


class TestGetRoutineEditorRoutineSpaces:
    """Tests: [GET] `/api/v1/routine-editor/routines/:routineId/spaces`"""

    def test_basic(
        self, client_live: StandardBotsRobot, routine_sample_id: str
    ) -> None:
        """Basic test: No globals"""
        client = client_live
        exclude_global_spaces = True

        with client.connection():
            res = client.routine_editor.routines.list_spaces(
                routine_id=routine_sample_id,
                exclude_global_spaces=exclude_global_spaces,
            )

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.SpacesPaginatedResponse)
        assert len(data.items) > 0

        # Routine should have good representation of space kinds: validate (de)serialization
        assert set(s.kind for s in data.items) == {
            "freeformPositionList",
            "plane",
            "singlePosition",
            "gridPositionList",
        }
        assert not any(True for s in data.items if s.is_global), "No globals expected"

    def test_include_globals(
        self, client_live: StandardBotsRobot, routine_sample_id: str
    ) -> None:
        """Include global spaces"""
        client = client_live
        exclude_global_spaces = False

        with client.connection():
            res = client.routine_editor.routines.list_spaces(
                routine_id=routine_sample_id,
                exclude_global_spaces=exclude_global_spaces,
            )

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.SpacesPaginatedResponse)
        assert len(data.items) > 0

        assert any(True for s in data.items if s.is_global), (
            "Globals not found but were expected"
        )
        assert any(True for s in data.items if not s.is_global), "No non-globals found"

    def test_bad_routine_id(self, client_live: StandardBotsRobot) -> None:
        """Bad routine ID"""
        client = client_live
        routine_id = "invalid"
        exclude_global_spaces = True

        with client.connection():
            res = client.routine_editor.routines.list_spaces(
                routine_id=routine_id,
                exclude_global_spaces=exclude_global_spaces,
            )

        assert res.isNotOk()
        assert res.status == 404
        assert isinstance(res.data, models.ErrorResponse)
        assert res.data.error == models.ErrorEnum.NotFound


class TestGetRoutineEditorRoutineStepVariables:
    """Tests: [GET] `/api/v1/routine-editor/routines/:routineId/step-variables`

    NOTE Tested best via code blocks.
    """

    @pytest.mark.routine_running
    @pytest.mark.parametrize(["step_id_map"], [(True,), (False,)])
    def test_routine_running(
        self,
        step_id_map: bool,
        client_live: StandardBotsRobot,
        routine_sample_id: str,
    ) -> None:
        """Routine loaded should generate state.

        NOTE Only runs when routine is running
        """
        client = client_live
        routine_id = routine_sample_id

        with client.connection():
            res = client.routine_editor.routines.get_step_variables(
                routine_id=routine_id,
                step_id_map=step_id_map,
            )

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.RoutineStepVariablesResponse)

        assert data.variables is not None
        assert isinstance(data.variables, dict)
        assert len(data.variables) > 0

        if step_id_map:
            assert data.step_id_map is not None
            assert isinstance(data.step_id_map, dict)
            assert len(data.step_id_map) > 0
        else:
            assert data.step_id_map is None

    def test_routine_not_running(
        self,
        client_live: StandardBotsRobot,
        routine_sample_id: str,
    ) -> None:
        """400 when not running"""
        client = client_live
        step_id_map = True  # Does not matter here.

        with client.connection():
            res = client.routine_editor.routines.get_step_variables(
                routine_id=routine_sample_id,
                step_id_map=step_id_map,
            )

        assert res.isNotOk()
        data = res.data
        assert isinstance(data, models.ErrorResponse)
        assert res.status == 400
        assert res.data.error == models.ErrorEnum.RoutineMustBeRunning


class TestGetRoutineEditorRoutineState:
    """Tests: [GET] `/api/v1/routine-editor/routines/:routineId/state`"""

    @pytest.mark.routine_running
    def test_routine_running(
        self,
        client_live: StandardBotsRobot,
        routine_sample_id: str,
    ) -> None:
        """Routine loaded should generate state.

        NOTE Only runs when routine is running
        """
        client = client_live
        routine_id = routine_sample_id

        with client.connection():
            res = client.routine_editor.routines.get_state(routine_id=routine_id)

        assert not res.isNotOk()
        data = res.data
        assert isinstance(data, models.RoutineStateResponse)

    def test_routine_not_loaded(self, client_live: StandardBotsRobot) -> None:
        """Routine is not loaded should fail"""
        client = client_live
        routine_id = "invalid"

        with client.connection():
            res = client.routine_editor.routines.get_state(routine_id=routine_id)

        assert res.isNotOk()
        data = res.data
        assert isinstance(data, models.ErrorResponse)
        assert res.status == 400
        assert res.data.error == models.ErrorEnum.RoutineMustBeRunning


@pytest.mark.skip("Not implemented")
class TestPostRoutineEditorRoutinePlay:
    """Tests: [POST] `/api/v1/routine-editor/routines/:routineId/play`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostRoutineEditorRoutinePause:
    """Tests: [POST] `/api/v1/routine-editor/routines/:routineId/pause`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostRoutineEditorStop:
    """Tests: [POST] `/api/v1/routine-editor/stop`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetRoutineEditorVariable:
    """Tests: [GET] `/api/v1/routine-editor/variables/:variableName`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostRoutineEditorVariable:
    """Tests: [POST] `/api/v1/routine-editor/variables/:variableName`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


class TestGetStatusControlMode:
    """Tests: [GET] `/api/v1/status/control-mode`

    Dependencies:
    - [x] DB
    - [ ] Robot context
    - [ ] Routine context
    """

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live

        with client.connection():
            res_raw = client.status.control.get_configuration_state_control()
        assert not res_raw.isNotOk()
        res = res_raw.ok()

        assert res.kind in {
            RobotControlModeEnum.RoutineEditor,
            RobotControlModeEnum.Api,
        }

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        client = client_sim

        with client.connection():
            res_raw = client.status.control.get_configuration_state_control()
        assert not res_raw.isNotOk()
        res = res_raw.ok()

        assert res.kind in {
            RobotControlModeEnum.RoutineEditor,
            RobotControlModeEnum.Api,
        }


@pytest.mark.skip("Control mode POST test does change the database")
class TestPostStatusControlMode:
    """Tests: [POST] `/api/v1/status/control-mode`"""

    """test_basic and test_basic_sim should be the same"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live

        with client.connection():
            control_mode_api = RobotControlMode(kind=RobotControlModeEnum.Api)
            client.status.control.set_configuration_control_state(control_mode_api)
            res_raw_api = client.status.control.get_configuration_state_control()
            res_api = res_raw_api.ok()
            assert res_api.kind == RobotControlModeEnum.Api

            control_mode_routine_editor = RobotControlMode(
                kind=RobotControlModeEnum.RoutineEditor
            )
            client.status.control.set_configuration_control_state(
                control_mode_routine_editor
            )
            res_raw_routine_editor = (
                client.status.control.get_configuration_state_control()
            )
            res_routine_editor = res_raw_routine_editor.ok()
            assert res_routine_editor.kind == RobotControlModeEnum.RoutineEditor


class TestGetStatusHealthHealth:
    """Tests: [GET] `/api/v1/status/health`

    Dependencies:
    - [x] DB
    - [ ] Robot context
    - [ ] Routine context
    """

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        client = client_live
        with client.connection():
            res_raw = client.status.health.get_health()
        assert not res_raw.isNotOk()
        res = res_raw.ok()

        assert isinstance(res, models.StatusHealthResponse)
        assert res.health == models.StatusHealthEnum.Ok

        # TODO How to test build ID + Name better?
        # (On dev machine is always None. On others it will always change.
        # Could do via a fixture?)
        # assert ok_res.build.id == None

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        client = client_sim
        with client.connection():
            res_raw = client.status.health.get_health()
        assert not res_raw.isNotOk()
        res = res_raw.ok()

        assert isinstance(res, models.StatusHealthResponse)
        assert res.health == models.StatusHealthEnum.Ok


@pytest.mark.skip("Not implemented")
class TestGetSpacePlanes:
    """Tests: [GET] `/api/v1/space/planes`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetIO:
    """Tests: [GET] `/api/v1/io`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostIO:
    """Tests: [POST] `/api/v1/io`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetJoints:
    """Tests: [GET] `/api/v1/joints`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostPosesCartesianPose:
    """Tests: [POST] `/api/v1/poses/cartesian-pose`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostPosesJointPose:
    """Tests: [POST] `/api/v1/poses/joint-pose`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostPosesPoseDistance:
    """Tests: [POST] `/api/v1/poses/pose-distance`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostPosesAdd:
    """Tests: [POST] `/api/v1/poses/add`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostPosesSubtract:
    """Tests: [POST] `/api/v1/poses/subtract`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetPosesJointsPosition:
    """Tests: [GET] `/api/v1/poses/joints-position`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetPosesTooltipPosition:
    """Tests: [GET] `/api/v1/poses/tooltip-position`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetPosesFlangePosition:
    """Tests: [GET] `/api/v1/poses/flange-position`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostPosesCartesianOffset:
    """Tests: [POST] `/api/v1/poses/cartesian-offset`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostInternalOnlyCreateRemoteControlAuthToken:
    """Tests: [POST] `/api/v1/internal-only/create-remote-control-auth-token`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostInternalOnlySpeechToText:
    """Tests: [POST] `/api/v1/internal-only/speech-to-text`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostInternalOnlyTextToSkill:
    """Tests: [POST] `/api/v1/internal-only/text-to-skill`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestGetIdentityBotIdentity:
    """Tests: [GET] `/api/v1/identity/bot_identity`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass


@pytest.mark.skip("Not implemented")
class TestPostApiSrvGraphQL:
    """Tests: [POST] `/api/v1/api-srv/graphql`"""

    def test_basic(self, client_live: StandardBotsRobot) -> None:
        """Basic test"""
        pass

    def test_basic_sim(self, client_sim: StandardBotsRobot) -> None:
        """Basic test: sim mode"""
        pass

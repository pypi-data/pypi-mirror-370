"""
Asyncio version of rbpodo
"""
from __future__ import annotations
import _rbpodo
import collections.abc
import numpy
import numpy.typing
import typing
__all__: list[str] = ['Cobot', 'CobotData', 'to_string']
class Cobot:
    def __init__(self, address: str, port: typing.SupportsInt = 5000) -> None:
        """
        Class is for interacting with Rainbow Robotics Cobot.
        
        Parameters
        ----------
        address : str
            IP address for command channel (e.g. 10.0.2.7). You can set up via teaching pendant (UI)
        port : int
            a port number for command channel (default: 5000).
        
        Example
        -------
        >>> robot = rb.cobot("10.0.2.7")
        >>> rc = rb.ResponseCollector()
        >>> robot.set_operation_mode(rc, rb.OperationMode.Real)
        """
    def activate(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        """
        Turn on the power supply for the robot arm. If the robot is already activated or has some errors, it returns immediately.
        
        Warning
        -------
        The robot arm will power up. Be careful when you use this function.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def arc_off(self, response_collector: _rbpodo.ResponseCollector, initial_wait: typing.SupportsFloat, welding_current: typing.SupportsFloat, voltage_out_condition: typing.SupportsInt, voltage: typing.SupportsFloat, wait_welding_finishing: typing.SupportsFloat, wait_after_finishing: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def arc_on(self, response_collector: _rbpodo.ResponseCollector, initial_wait: typing.SupportsFloat, speed: typing.SupportsFloat, accel: typing.SupportsFloat, welding_current: typing.SupportsFloat, voltage_out_condition: typing.SupportsInt, voltage: typing.SupportsFloat, use_arc_timeout: typing.SupportsInt, arc_timeout: typing.SupportsFloat, wait_after_arc: typing.SupportsFloat, when_pause: typing.SupportsInt, speed_bar_under_arc: typing.SupportsInt, arc_retries: typing.SupportsInt, retries_interval: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def arc_sensing_off(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def arc_sensing_on(self, response_collector: _rbpodo.ResponseCollector, sensing_input_channel: typing.SupportsInt, tracking_target_value: typing.SupportsInt, dt1: typing.SupportsFloat, dt2: typing.SupportsFloat, frame: typing.SupportsInt, axis: typing.SupportsInt, tracking_gain: typing.SupportsFloat, variation_limit: typing.SupportsFloat, lpf: typing.SupportsFloat, variation_speed_limit: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def arc_set(self, response_collector: _rbpodo.ResponseCollector, speed: typing.SupportsFloat, accel: typing.SupportsFloat, welding_current: typing.SupportsFloat, voltage_out_condition: typing.SupportsInt, voltage: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    @typing.overload
    def calc_fk_tcp(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], j0: typing.SupportsFloat, j1: typing.SupportsFloat, j2: typing.SupportsFloat, j3: typing.SupportsFloat, j4: typing.SupportsFloat, j5: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Calculate TCP posture w.r.t. global (base) coordinate from six joint angles.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            TCP pose [x, y, z, rx, ry, rz] w.r.t. global (base) coordinate
        j0, j1, j2, j3, j4, j5: joint angles (unit: degree)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> pnt = np.zeros((6,))
        >>> res = robot.calc_fk_tcp(rc, pnt, 0, 0, 0, 0, 0, 0)
        """
    @typing.overload
    def calc_fk_tcp(self, response_collector: _rbpodo.ResponseCollector, j0: typing.SupportsFloat, j1: typing.SupportsFloat, j2: typing.SupportsFloat, j3: typing.SupportsFloat, j4: typing.SupportsFloat, j5: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Calculate TCP posture w.r.t. global (base) coordinate from six joint angles.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        j0, j1, j2, j3, j4, j5: joint angles (unit: degree)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        numpy.ndarray(shape=(6, 1))
            TCP pose [x, y, z, rx, ry, rz] w.r.t. global (base) coordinate
        
        
        Examples
        --------
        >>> [res, pnt] = robot.calc_fk_tcp(rc, 0, 0, 0, 0, 0, 0, -1, False)
        """
    @typing.overload
    def calc_fk_tcp(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.ArrayLike, numpy.float64], joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Calculate TCP posture w.r.t. global (base) coordinate from six joint angles.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        [out] point : numpy.ndarray(shape=(6, 1))
            TCP pose [x, y, z, rx, ry, rz] w.r.t. global (base) coordinate
        joint : numpy.ndarray(shape=(6, 1))
            Single joint type variable which contains six joint-angles.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> pnt = np.zeros((6,))
        >>> res = robot.calc_fk_tcp(rc, pnt, np.zeros((6,)))
        """
    @typing.overload
    def calc_fk_tcp(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Calculate TCP posture w.r.t. global (base) coordinate from six joint angles.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        joint : numpy.ndarray(shape=(6, 1))
            Single joint type variable which contains six joint-angles.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        point : numpy.ndarray(shape=(6, 1))
            TCP pose [x, y, z, rx, ry, rz] w.r.t. global (base) coordinate
        
        Examples
        --------
        >>> [res, pnt] = robot.calc_fk_tcp(rc, np.zeros((6,)))
        """
    def disable_waiting_ack(self, response_collector: _rbpodo.ResponseCollector) -> typing.Any:
        ...
    def enable_waiting_ack(self, response_collector: _rbpodo.ResponseCollector) -> typing.Any:
        ...
    def eval(self, response_collector: _rbpodo.ResponseCollector, script: str, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        A function that evaluates a script on the 'Cobot'.
        
        This function sends the given script to the 'Cobot' for evaluation and waits for the response from the 'Cobot'. In the case of failure, the function returns 'Timeout' or 'Error'.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        script : str
            The script to be evaluated.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def flush(self, response_collector: _rbpodo.ResponseCollector) -> typing.Any:
        ...
    def get_control_box_info(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Retrieves information about the control box.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        ControlBoxInfo
            Information including "system version" and "robot box type"
        
        Examples
        --------
        >>> res, info = robot.get_control_box_info(rc)
        >>> print(info)
        { "SystemVersion": 24021504, "RobotBoxType": 11 }
        """
    def get_robot_state(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def get_system_variable(self, response_collector: _rbpodo.ResponseCollector, system_variable: _rbpodo.SystemVariable, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def get_tcp_info(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        This function returns the TCP information of the current robot.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        numpy.ndarray(shape=(6, 1))
            TCP of the current robot with respect to the global coordinate system. (Unit: mm & degree)
        
        
        Examples
        --------
        >>> [res, pnt] = robot.get_tcp_info(rc)
        """
    def get_tfc_info(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        This function returns the TFC (Tool flange center) information of the current robot.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        numpy.ndarray(shape=(6, 1))
            TFC of the current robot based on the global coordinate system. (Unit: mm & degree)
        
        
        Examples
        --------
        >>> [res, pnt] = robot.get_tfc_info(rc)
        """
    def gripper_inspire_humanoid_hand_initialization(self, response_collector: _rbpodo.ResponseCollector, reading_data_type: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_inspire_humanoid_hand_set_finger(self, response_collector: _rbpodo.ResponseCollector, function: typing.SupportsInt, little: typing.SupportsInt, ring: typing.SupportsInt, middle: typing.SupportsInt, index: typing.SupportsInt, thumb1: typing.SupportsInt, thumb2: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_koras_tooling_core_initialization(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, target_torque: typing.SupportsInt, target_speed: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_koras_tooling_finger_goto(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, target_position: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_koras_tooling_finger_initialization(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_koras_tooling_finger_open_close(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, finger_open_close: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_koras_tooling_vaccum_control(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, vaccum_on_off: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_rts_rhp12rn_force_control(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, target_force_ratio: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_rts_rhp12rn_position_control(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, target_position_ratio: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_rts_rhp12rn_select_mode(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, force: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def gripper_rts_rhp12rn_set_force_limit(self, response_collector: _rbpodo.ResponseCollector, conn_point: _rbpodo.GripperConnectionPoint, limit: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def move_c_axis(self, response_collector: _rbpodo.ResponseCollector, center: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], x_axis: typing.SupportsFloat, y_axis: typing.SupportsFloat, z_axis: typing.SupportsFloat, angle: typing.SupportsFloat, speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, option: _rbpodo.MoveCRotationOption, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function performs a movement that draws an arc through via & target points.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        center : numpy.ndarray(shape=(6, 1))
            Center of the rotation (Unit: mm)
        x_axis : float
            Rotation axis's x axis vector
        y_axis : float
            Rotation axis's y axis vector
        z_axis : float
            Rotation axis's z axis vector
        angle : float
            Rotation angle (Unit: deg)
        speed : float
            Speed (Unit: mm/s)
        acceleration : float
            Acceleration (Unit: mm/s^2)
        option : MoveCRotationOption
            Rotation options. (0 : Intended, 1 : Constant, 2 : Radial)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> robot.move_c_axis(rc, {200, 200, 200, 0, 0, 0}, 1, 0, 0, 180, 50, 10, 2)
        >>> # Rotate 180 degrees around the x-axis. Center of rotation is '{200, 200, 200, 0, 0, 0}'. Based on the center point of the rotation, the orientation of the TCP is changed together.
        """
    def move_c_points(self, response_collector: _rbpodo.ResponseCollector, via_point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], target_point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, option: _rbpodo.MoveCOrientationOption, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function performs a movement that draws an arc through via & target points.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        via_point : numpy.ndarray(shape=(6, 1))
            via Point TCP posture.
        target_point: numpy.ndarray(shape=(6, 1))
            target Point TCP posture.
        speed : float
            Speed (Unit: mm/s)
        acceleration : float
            Acceleration (Unit: mm/s^2)
        option : MoveCOrientationOption
            Orientation options. (0 : Intended, 1 : Constant, 2 : Radial, 3 : Smooth)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_itpl_add(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function adds the points used in MoveITPL to the list.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP posture. (Point)
        speed : float
            Speed (Unit: mm/s)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_itpl_clear(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Initialize (Clear) the point list to be used in MoveITPL.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_itpl_run(self, response_collector: _rbpodo.ResponseCollector, acceleration: typing.SupportsFloat, option: _rbpodo.MoveITPLOption, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function executes MoveITPL using the points added in move_itpl_add.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        acceleration : float
            Acceleration
        option : MoveITPLOption
            Orientation/motion option. (CA : Combined Arc mode)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_j(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_err: bool = False) -> typing.Any:
        """
        Move the robot arm to the target joint angle in joint space.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        joint : numpy.ndarray(shape=(6, 1))
            Target joint angles. (Joint)
        speed : float
            Speed (Unit: deg/s)
        acceleration : float
            Acceleration (Unit: deg/s^2)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> robot.move_j(rc, {0, 0, 90, 0, 90, 0}, 60, 80) // move joint angles to (0,0,90,0,90,0) degree with speed/acceleration = 60/80.
        """
    def move_jb2_add(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, blending_value: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_err: bool = False) -> typing.Any:
        ...
    def move_jb2_clear(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1, return_on_err: bool = False) -> typing.Any:
        ...
    def move_jb2_run(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1, return_on_err: bool = False) -> typing.Any:
        ...
    def move_jb_add(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function adds the joint-angles used in MoveJB to the list.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        joint : numpy.ndarray(shape=(6, 1))
            Target joint angles (Unit: deg)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_jb_clear(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Initialize (Clear) the point list to be used in MoveJB.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_jb_run(self, response_collector: _rbpodo.ResponseCollector, speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function executes MoveJB using the points added in move_jb_add.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        speed : float
            Speed (Unit: deg/s)
        acceleration : float
            Acceleration (Unit: deg/s^2)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_jl(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_err: bool = False) -> typing.Any:
        """
        This function moves to the target point using the move_j method rather than a straight line.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP posture. (Point)
        speed : float
            Speed (Unit: deg/s)
        acceleration : float
            Acceleration (Unit: deg/s^2)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> robot.move_jl(rc, {100, 200, 300, 0, 0, 0}, 20, 5) // Move TCP to '{x = 100, y = 200, z = 300, rx = 0, ry = 0, rz = 0}' via MoveJ method.
        """
    def move_l(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_err: bool = False) -> typing.Any:
        """
        A function that makes TCP to move in a straight line to the target point.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP pose
        speed : float
            Speed (unit: mm/s)
        acceleration : float
            Acceleration (unit: mm/s^2)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> my_point1 = np.array([100, 200, 300, 0, 0, 0])
        >>> my_point2 = np.array([100, 150, 100, 0, 90, 0])
        >>> robot.move_l(rc, my_point1, 20, 5)
        >>> robot.move_l(rc, my_point2, 20, 5)
        """
    def move_l_rel(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, frame: _rbpodo.ReferenceFrame, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        A function that makes TCP to move in a straight line to the target point.
        Enter the target point as a value relative to the current TCP value.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP pose
        speed : float
            Speed (unit: mm/s)
        acceleration : float
            Acceleration (unit: mm/s^2)
        frame : ReferenceFrame
            Reference frame for the relative point value.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> target_point = np.array([0, 100, -200, 0, 0, 0])
        >>> robot.move_l_rel(rc, target_point, 300, 400, rb.ReferenceFrame.Base) # move TCP (0,100,-200) w.r.t. Base coordinate (speed/acceleration = 300 / 400)
        """
    def move_lb_add(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], blend_distance: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function adds the points used in MoveLB to the list.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP posture. (Point)
        blend_distance : float
            Blend distance. (Unit: mm)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_lb_clear(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Initialize (Clear) the point list to be used in MoveLB.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_lb_run(self, response_collector: _rbpodo.ResponseCollector, speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, option: _rbpodo.MoveLBOption, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function executes MoveLB using the points added in move_lb_add.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        speed : float
            Speed (Unit: mm/s)
        acceleration : float
            Acceleration (Unit: mm/s^2)
        option : MoveLBOption
            Orientation options. (0 : Intended, 1 : Constant)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_lc_add(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, property: _rbpodo.MoveLCProperty, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function adds the points used in MoveLC to the list.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP posture. (Point)
        speed : float
            Speed (Unit: mm/s)
        property : MoveLCProperty
            0 or 1 (0 : Pass through linear motion, 1 : Pass through circular motion)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_lc_clear(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Initialize (Clear) the point list to be used in MoveLC.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_lc_run(self, response_collector: _rbpodo.ResponseCollector, acceleration: typing.SupportsFloat, option: _rbpodo.MoveLCOption, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function executes MoveITPL using the points added in move_itpl_add.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        acceleration : float
            Acceleration
        option : MoveLCOption
            Orientation options
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_pb_add(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], speed: typing.SupportsFloat, option: _rbpodo.BlendingOption, blending_value: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        This function adds the points used in MovePB to the list.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            Target TCP posture. (Point)
        speed : float
            Speed (Unit: mm/s)
        option : BlendingOption
            Blending option (0: blend based on ratio, 1: blend based on distance.)
        blending_value : float
            Blending value (0~1 in ratio option or distance in distance option (Unit: mm)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> robot.move_pb_clear(rc)
        >>> robot.move_pb_add(rc, np.array([100, 200, 200, 90, 0, 0]), 200.0, rb.BlendingOption.Ratio, 0.5)
        >>> robot.move_pb_add(rc, np.array([300, 300, 400, 0, 0, 0]), 400.0, rb.BlendingOption.Ratio, 0.5)
        >>> robot.move_pb_add(rc, np.array([0, 200, 400, 90, 0, 0]), 200.0, rb.BlendingOption.Ratio, 0.5)
        >>> robot.move_pb_run(rc, 800, rb.MovePBOption.Intended)
        """
    def move_pb_clear(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        Initialize (Clear) the point list to be used in MovePB.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_pb_run(self, response_collector: _rbpodo.ResponseCollector, acceleration: typing.SupportsFloat, option: _rbpodo.MovePBOption, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        """
        This function executes MovePB using the points added in move_pb_add.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        acceleration : float
            Acceleration (Unit: mm/s^2)
        option : MovePBOption
            Orientation option (0: Intended, 1: Constant)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def move_servo_j(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], t1: typing.SupportsFloat, t2: typing.SupportsFloat, gain: typing.SupportsFloat, alpha: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def move_servo_l(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], t1: typing.SupportsFloat, t2: typing.SupportsFloat, gain: typing.SupportsFloat, alpha: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def move_servo_t(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], t1: typing.SupportsFloat, t2: typing.SupportsFloat, compensation: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def move_speed_j(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], t1: typing.SupportsFloat, t2: typing.SupportsFloat, gain: typing.SupportsFloat, alpha: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def move_speed_l(self, response_collector: _rbpodo.ResponseCollector, joint: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], t1: typing.SupportsFloat, t2: typing.SupportsFloat, gain: typing.SupportsFloat, alpha: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def multi_directional_arc_sensing_off(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def multi_directional_arc_sensing_on(self, response_collector: _rbpodo.ResponseCollector, sensing_input_channel: typing.SupportsInt, t1: typing.SupportsInt, t2: typing.SupportsInt, lpf: typing.SupportsFloat, fd_Kp: typing.SupportsFloat, fd_Ki: typing.SupportsFloat, fd_anti_wind_rate: typing.SupportsFloat, fd_max_deviation: typing.SupportsFloat, wd_Kp: typing.SupportsFloat, wd_Ki: typing.SupportsFloat, wd_anti_wind_rate: typing.SupportsFloat, wd_max_deviation: typing.SupportsFloat, average_window: typing.SupportsFloat, weaving_direction_rate: typing.SupportsFloat, weaving_direction_reference: typing.SupportsFloat, weighting_mode: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def print_variable(self, response_collector: _rbpodo.ResponseCollector, variable_name: str, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def rt_script(self, response_collector: _rbpodo.ResponseCollector, single_command: str, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def rt_script_onoff(self, response_collector: _rbpodo.ResponseCollector, on: bool, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def set_acc_multiplier(self, response_collector: _rbpodo.ResponseCollector, multiplier: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Sets the overall acceleration multiplier.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        multiplier : float
            Multiply variable. (0~2) Default value is 1.0.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_box_aout(self, response_collector: _rbpodo.ResponseCollector, port: typing.SupportsInt, voltage: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the analog output of the control box.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        port : int
            Port number for the analog output. (0~15)
        voltage : float
            Desired output voltage (0~10V, Unit: V)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_box_dout(self, response_collector: _rbpodo.ResponseCollector, port: typing.SupportsInt, mode: _rbpodo.DigitalIOMode, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the digital output of the control box.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        port : int
            Port number for the digital output.
        mode : DigitalIOMode
            Output mode selection
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_box_dout_toggle(self, response_collector: _rbpodo.ResponseCollector, port: typing.SupportsInt, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Toggles the current digital output of the control box.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        port : int
            Port number for the analog output. (0~15)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_collision_after(self, response_collector: _rbpodo.ResponseCollector, mode: _rbpodo.CollisionFollowUpMode, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the program flow direction after the collision detection.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        mode : CollisionReactionMode
            A variable represents a stop mode.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_collision_mode(self, response_collector: _rbpodo.ResponseCollector, mode: _rbpodo.CollisionMode, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the stop-mode after the collision detection.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        mode : CollisionMode
            The variable represents a stop mode.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_collision_onoff(self, response_collector: _rbpodo.ResponseCollector, on: bool, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        This function turns on/off the collision detection function.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        on : bool
            The variable represents an on/off state, where 0 is off and 1 is on.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_collision_threshold(self, response_collector: _rbpodo.ResponseCollector, threshold: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Sets the collision sensitivity (threshold).
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        threshold : float
            The variable represents an threshold value. The lower the value, the more sensitive to collision. (0~1)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_dout_bit_combination(self, response_collector: _rbpodo.ResponseCollector, first_port: typing.SupportsInt, last_port: typing.SupportsInt, value: typing.SupportsInt, mode: _rbpodo.Endian, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the digital outputs of the control box simultaneously.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        first_port : int
            First port number (0~15)
        last_port : int
            Last port number (0~15)
            last_port must be greater or equal than first_port.
        value : int
            Output value for digital ports (bit combination)
            If mode is LittleEndian and value is 5, then port 0 and port 2 will be high.
        mode : rbpodo.Endian
            Endian selection
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> robot.set_dout_bit_combination(rc, 0, 15, 5, rb.Endian.LittleEndian)  # Port 0 and 2 will be high, while port 1 and 3 are low
        >>> robot.set_dout_bit_combination(rc, 0, 15, 10, rb.Endian.LittleEndian) # Port 1 and 3 will be high, while port 0 and 2 are low
        """
    def set_freedrive_mode(self, response_collector: _rbpodo.ResponseCollector, on: bool, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        ...
    def set_operation_mode(self, response_collector: _rbpodo.ResponseCollector, mode: _rbpodo.OperationMode, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Change the operation mode between real and simulation modes.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        mode : rbpodo.OperationMode
            If set to OperationMode.Real, the robot moves when commanded.
            If set to OperationMode.Simulation, the robot does not moves but the internal reference values changes.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_payload_info(self, response_collector: _rbpodo.ResponseCollector, weight: typing.SupportsFloat, com_x: typing.SupportsFloat, com_y: typing.SupportsFloat, com_z: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the tool payload w.r.t. the manufacturer’s default tool coordinate system.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        weight : float
            payload weight (Unit: Kg)
        com_x : float
            payload center of mass x-axis value with respect to the manufacturer's default coordinate system. (Unit: mm)
        com_y : float
            payload center of mass y-axis value with respect to the manufacturer's default coordinate system. (Unit: mm)
        com_z : float
            payload center of mass z-axis value with respect to the manufacturer's default coordinate system. (Unit: mm)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_serial_box(self, response_collector: _rbpodo.ResponseCollector, baud_rate: typing.SupportsInt, stop_bit: typing.SupportsInt, parity_bit: typing.SupportsInt, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the serial communication (RS232/485) provided by the control box.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        baud_rate : int
            Communication speed (Baud rate)
        stop_bit : int
            Stop bit, (0 or 1, Default value is 1)
        parity_bit : int
            Parity bit, (0: none, 1: odd, 2: even, Default value is 0)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_serial_tool(self, response_collector: _rbpodo.ResponseCollector, baud_rate: typing.SupportsInt, stop_bit: typing.SupportsInt, parity_bit: typing.SupportsInt, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the serial communication (RS232/485) provided by the Tool Flange of the robot arm.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        baud_rate : int
            Communication speed (Baud rate)
        stop_bit : int
            Stop bit, (0 or 1, Default value is 1)
        parity_bit : int
            Parity bit, (0: none, 1: odd, 2: even, Default value is 0)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> robot.set_serial_tool(rc, 115200, 1, 0) # Set tool-flange serial comm. : baud rate = 115200 / stop bit = 1 / parity = none
        """
    def set_speed_acc_j(self, response_collector: _rbpodo.ResponseCollector, speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Sets fixed joint velocity/acceleration for J-series motions (MoveJ, MoveJB, MoveJL).
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        speed : float
            Speed/velocity (Unit: deg/s). Does not use negative value.
        acceleration : float
            Acceleration (Unit: deg/s^2). Does not use negative value.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_speed_acc_l(self, response_collector: _rbpodo.ResponseCollector, speed: typing.SupportsFloat, acceleration: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Sets fixed linear velocity/acceleration for L-series motions (MoveL, MovePB, MoveLB, MoveITPL).
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        speed : float
            Speed/velocity (Unit: mm/s)
        acceleration : float
            Acceleration (Unit: mm/s^2)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_speed_bar(self, response_collector: _rbpodo.ResponseCollector, speed: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the overall speed control bar. (bottom speed control bar in UI).
        
        Warning
        -------
        When running a program on the UI Make page, this function does not work if the safety slide bar option is turned on.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        speed : float
            Desired speed control bar position (0~1)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_speed_multiplier(self, response_collector: _rbpodo.ResponseCollector, multiplier: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Sets the overall speed (velocity) multiplier.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        multiplier : float
            Multiply variable. (0~2) Default value is 1.0.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_tcp_info(self, response_collector: _rbpodo.ResponseCollector, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the TCP position and orientation w.r.t. the manufacturer’s default tool coordinate system.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        point : numpy.ndarray(shape=(6, 1))
            position and orientation of tcp with respect to manufacturer's default tool coordinate system. (x, y, z, rx, ry, rz) (Unit: mm & degree)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_tool_box(self, response_collector: _rbpodo.ResponseCollector, x_width: typing.SupportsFloat, y_width: typing.SupportsFloat, z_width: typing.SupportsFloat, x_offset: typing.SupportsFloat, y_offset: typing.SupportsFloat, z_offset: typing.SupportsFloat, timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set the tool box w.r.t. the manufacturer’s default tool coordinate system.
        
        Warning
        -------
        The value set in this function returns to the default value after the program ends.
        If this function is not called in program-flow, the value set in the Setup page is used.
        During program flow, the value set in this function is maintained until this function is called again.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        x_width : float
            width of tool along x-axis with respect to the manufacturer's default tool coordinate system. (Unit: mm)
        y_width : float
            width of tool along y-axis with respect to the manufacturer's default tool coordinate system. (Unit: mm)
        z_width : float
            width of tool along z-axis with respect to the manufacturer's default tool coordinate system. (Unit: mm)
        x_offset : float
            offset of box along x-axis with respect to the manufacturer's default tool coordinate system. (Unit: mm)
        y_offset : float
            offset of box along y-axis with respect to the manufacturer's default tool coordinate system. (Unit: mm)
        z_offset : float
            offset of box along z-axis with respect to the manufacturer's default tool coordinate system. (Unit: mm)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def set_tool_out(self, response_collector: _rbpodo.ResponseCollector, voltage: typing.SupportsInt, signal_0: typing.SupportsInt, signal_1: typing.SupportsInt, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def set_user_coordinate(self, response_collector: _rbpodo.ResponseCollector, id: typing.SupportsInt, point: typing.Annotated[numpy.typing.NDArray[numpy.float64], "[6, 1]"], timeout: typing.SupportsFloat = -1, return_on_error: bool = False) -> typing.Any:
        """
        Set user coordinate
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        id : int
            id of user coordinate to change (0~2)
        point : numpy.ndarray(shape=(6, 1))
            position and orientation of coordinate with respect to base frame. (x, y, z, rx, ry, rz) (Unit: mm & degree)
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def shutdown(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        """
        Turn off the power supply for the robot arm.
        
        Warning
        -------
        The robot arm powers up. Be careful when you use this function.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        """
    def task_load(self, response_collector: _rbpodo.ResponseCollector, program_name: str, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def task_pause(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def task_play(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def task_resume(self, response_collector: _rbpodo.ResponseCollector, collision: bool, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def task_stop(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def tcp_weave_off(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def tcp_weave_on(self, response_collector: _rbpodo.ResponseCollector, type: typing.SupportsInt, torch_axis: typing.SupportsInt, weaving_axis: typing.SupportsInt, frame_tilt: typing.SupportsFloat, frame_rot: typing.SupportsFloat, frame_distort: typing.SupportsFloat, mag_1: typing.SupportsFloat, mag_2: typing.SupportsFloat, vel_1: typing.SupportsFloat, vel_2: typing.SupportsFloat, t1: typing.SupportsFloat, t2: typing.SupportsFloat, t3: typing.SupportsFloat, t4: typing.SupportsFloat, scale_y: typing.SupportsFloat, offset_y: typing.SupportsFloat, bending: typing.SupportsFloat, swing: typing.SupportsFloat, frame_option: typing.SupportsFloat, drag_rate: typing.SupportsFloat, user_Rx: typing.SupportsFloat, user_Ry: typing.SupportsFloat, user_Rz: typing.SupportsFloat, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def wait_for_move_finished(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        ...
    def wait_for_move_started(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        """
        Wait until the motion is started.
        
        More specifically, the program is waiting for the response message from control box ``info[motion_changed][X]`` where ``X`` is positive integer.
        
        Parameters
        ----------
        response_collector : ResponseCollector
            A collector object to accumulate and manage the response message.
        timeout : float
            The maximum duration (in seconds) to wait for a response before timing out.
        return_on_error : bool
            A boolean flag indicating whether the function should immediately return upon encountering an error.
        
        Returns
        -------
        ReturnType
        
        Examples
        --------
        >>> joint = np.array([0, 0, 0, 0, 0, 0])
        >>> robot.move_j(rc, joint, 60, 80)
        >>> rc = rc.error().throw_if_not_empty()
        >>> if robot.wait_for_move_started(rc).type() == rb.ReturnType.Success:
        >>>     robot.wait_for_move_finished(rc)
        """
    def wait_for_task_finished(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        ...
    def wait_for_task_loaded(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        ...
    def wait_for_task_started(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = True) -> typing.Any:
        ...
    def wait_until(self, response_collector: _rbpodo.ResponseCollector, func: collections.abc.Callable[[_rbpodo.Response], bool], timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
    def wait_until_ack_message(self, response_collector: _rbpodo.ResponseCollector, timeout: typing.SupportsFloat = -1.0, return_on_error: bool = False) -> typing.Any:
        ...
class CobotData:
    def __init__(self, address: str, port: typing.SupportsInt = 5001) -> None:
        ...
    def request_data(self, timeout: typing.SupportsFloat = -1.0) -> typing.Any:
        ...
def to_string(type: _rbpodo.Response.Type) -> str:
    ...

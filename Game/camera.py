"""New Impressive Title - Camera API"""

from direct.task.Task import Task
from kivy.logger import Logger
from panda3d.core import CollisionNode, CollisionSphere, Vec3


#Constants
#==============================================================================
CAM_MODE_FIRST_PERSON = 0
CAM_MODE_CHASE = 1
CAM_MODE_FREE = 2


#Classes
#==============================================================================
class CameraManager(object):
    """A high-level camera manager. Manages camera mode and movement."""
    def __init__(self):
        """Setup this camera manager."""
        Logger.info("Initializing camera manager...")
        self.reset()

        #Camera Controls
        #===============
        #F1 - first person view
        #F2 - chase cam view
        #F3 - free cam view
        #W - move forward
        #S - move backward
        #A - move left
        #D - move right
        #R - rise
        #F - fall
        #Up - look up
        #Down - look down
        #Left - turn left
        #Right - turn right
        base.accept("f1", self.change_mode, [CAM_MODE_FIRST_PERSON])
        base.accept("f2", self.change_mode, [CAM_MODE_CHASE])
        base.accept("f3", self.change_mode, [CAM_MODE_FREE])

        base.accept("w", self.set_move_vec_y, [.2 * self.speed])
        base.accept("w-up", self.set_move_vec_y, [0])
        base.accept("s", self.set_move_vec_y, [-.2 * self.speed])
        base.accept("s-up", self.set_move_vec_y, [0])
        base.accept("a", self.set_move_vec_x, [-.2 * self.speed])
        base.accept("a-up", self.set_move_vec_x, [0])
        base.accept("d", self.set_move_vec_x, [.2 * self.speed])
        base.accept("d-up", self.set_move_vec_x, [0])
        base.accept("r", self.set_move_vec_z, [.2 * self.speed])
        base.accept("r-up", self.set_move_vec_z, [0])
        base.accept("f", self.set_move_vec_z, [-.2 * self.speed])
        base.accept("f-up", self.set_move_vec_z, [0])

        base.accept("arrow_up", self.set_rot_vec_p, [.5])
        base.accept("arrow_up-up", self.set_rot_vec_p, [0])
        base.accept("arrow_down", self.set_rot_vec_p, [-.5])
        base.accept("arrow_down-up", self.set_rot_vec_p, [0])
        base.accept("arrow_left", self.set_rot_vec_h, [.5])
        base.accept("arrow_left-up", self.set_rot_vec_h, [0])
        base.accept("arrow_right", self.set_rot_vec_h, [-.5])
        base.accept("arrow_right-up", self.set_rot_vec_h, [0])

        #Setup collision detection
        cnode = CollisionNode("camera")
        cnode.add_solid(CollisionSphere(0, 0, 0, 10))
        self.collider = base.camera.attach_new_node(cnode)
        base.cTrav.add_collider(self.collider, base.portal_handler)

        #Start camera manager task
        base.task_mgr.add(self.run_logic)
        Logger.info("Camera manager initialized.")

    def reset(self):
        """Reset this camera manager."""
        self.mode = CAM_MODE_FIRST_PERSON
        self.speed = 10
        self.move_vec = Vec3(0, 0, 0)
        self.rot_vec = Vec3(0, 0, 0)

        base.disable_mouse()
        base.camera.set_pos(0, 0, 0)
        base.camera.set_hpr(0, 0, 0)

    def change_mode(self, mode):
        """Change the current camera mode."""
        self.mode = mode

        if mode == CAM_MODE_FIRST_PERSON:
            Logger.info("Camera mode changed to first person cam.")

        elif mode == CAM_MODE_CHASE:
            Logger.info("Camera mode changed to chase cam.")

        elif mode == CAM_MODE_FREE:
            Logger.info("Camera mode changed to free cam.")

    def set_move_vec_x(self, x):
        """Set the X movement vector of the camera. This is only used in free
        mode.
        """
        self.move_vec.x = x

    def set_move_vec_y(self, y):
        """Set the Y movement vector of the camera. This is only used in free
        mode.
        """
        self.move_vec.y = y

    def set_move_vec_z(self, z):
        """Set the Z movement vector of the camera. This is only used in free
        mode.
        """
        self.move_vec.z = z

    def set_rot_vec_h(self, h):
        """Set the heading rotation vector of the camera. This is only used in
        free mode.
        """
        self.rot_vec.x = h

    def set_rot_vec_p(self, p):
        """Set the pitch rotation vector of the camera."""
        self.rot_vec.y = p

    def run_logic(self, task):
        """Run the logic for this camera manager."""
        #We only need to execute logic for the free camera here
        if self.mode == CAM_MODE_FREE:
            #Update rotation first
            base.camera.set_hpr(base.camera.get_hpr() + self.rot_vec)

            #Now update position
            pos = base.camera.get_pos()
            vec = Vec3(self.move_vec.x, self.move_vec.y, 0)
            base.camera.set_pos(pos + base.camera.get_quat(render).xform(vec))
            base.camera.set_z(base.camera.get_z() + self.move_vec.z)

        #Continue this task infinitely
        return Task.cont

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os


# Constants defined for controlling cooldowns

TIMES_B4_COOLDOWN = 5
COOLDOWN_TIME_STANDARD = 15
COOLDOWN_TIME_HOUR = 3600
COOLDOWN_TIME_10_MIN = 600
HOURS_IN_WEEK = 168

# Constants for general discord things

MAX_AUDIT_QUERY = 1000

# Constants to define users, roles and channels. Note that users are supposed
# to be set as environment variables for privacy reasons.

ID_ABUSED = int(os.environ["THE_ABUSED"])
ID_ABUSER = int(os.environ["THE_ABUSER"])
ID_USER_WORD = int(os.environ["ZADETH"])
ID_BOT_IGNORE = int(os.environ["BOT_IGNORE"])
ID_SERVER = 237647756049514498
ID_ROLE_SUB = 799243498091577366
ID_ROLE_MAIN = 265251835432927232
ID_MAIN_CHANNEL = 237647756049514498
ID_SPAM_CHANNEL = 816381916361916416
ID_WL_CHANNEL = 819577977998147604

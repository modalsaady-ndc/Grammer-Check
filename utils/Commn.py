# common.py


from Config.config import Config, DevConfig, SQLConfig
from Services.TokenSAdmin import CheckTokenSA
from Services.TokenOAdmin import CheckTokenOA
from Services.TokenROUser import CheckTokenROU
from Services.TokenWOUser import CheckTokenWOU
from Services.Req_Rep import ReqRep
from Services.Permissionview import PV
from Services.UserTable import UserTable
from Services.parentchildorgs import arrange_childorg_hierarchy, arrange_parentorg_hierarchy
from flask import Flask, request, jsonify, current_app, make_response, abort, Response, send_file
from flask_restx import Resource, Namespace, fields, marshal
from flask_paginate import Pagination, get_page_parameter
from Models.Orgs_Links import Link, Orgs
from Models.Contrain_models import contraindications, Req_Rep, Types, Req_Rep, LinkCon
from Models.Users_model import User, AccessToken, Permission, PermissionView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
        JWTManager, create_access_token,
        create_refresh_token, jwt_required,
        get_jwt, verify_jwt_in_request,
        get_jwt_identity, unset_jwt_cookies
    )

from datetime import datetime
from sqlalchemy import join
from math import log, floor
from exts import db
import os
import random
import string
import traceback
import pyodbc
import json
import math
import base64







import re
from datetime import datetime


class LoginValidator:
    """
    A class to handle the validation of login request fields like UsUsername and UsPassword.
    """

    @staticmethod
    def check_password_complexity(password):
        """
        Checks the complexity of the password.
        - At least one lowercase letter, one uppercase letter, one digit, and one special character.
        """
        if len(password) < 8:
            return "يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل"
        if not re.search(r'[A-Z]', password):
            return "يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل"
        if not re.search(r'[a-z]', password):
            return "يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل"
        if not re.search(r'[0-9]', password):
            return "يجب أن تحتوي كلمة المرور على رقم واحد على الأقل"
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return "يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل"
        return "ok"

    @staticmethod
    def validate_ususername(data):
        """
        Validates the 'UsUsername' field.
        - Must be present in the request.
        - Must contain only English letters.
        """
        ususername = data.get('UsUsername')
        
        # Check if UsUsername is provided
        if not ususername:
            return {'error': 'اسم المستخدم مطلوب في الطلب'}, 400
        
        # # Check if UsUsername contains only English letters
        # if not re.match(r'^[A-Za-z0-9._-]+$', ususername):
        #     return {'error': 'يجب أن يحتوي اسم المستخدم على أحرف إنجليزية فقط'}, 400
        
        # Check if UsUsername contains Arabic letters
        if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', ususername):
            return {'error': 'يجب ألا يحتوي اسم المستخدم على أحرف عربية'}, 400

        # If validation passes, return None (indicating no errors)
        return None

    @staticmethod
    def validate_uspassword(data):
        """
        Validates the 'UsPassword' field.
        - Must be present in the request.
        - Must meet the complexity requirements.
        """
        uspassword = data.get('UsPassword')

        # Check if UsPassword is provided
        if not uspassword:
            return {'error': 'كلمة المرور مطلوبة في الطلب'}, 400

        # Check password complexity
        complexity_message = LoginValidator.check_password_complexity(uspassword)
        if complexity_message != "ok":
            return {'error': complexity_message}, 400

        # If validation passes, return None (indicating no errors)
        return None

    @staticmethod
    def validate_login_data(data):
        """
        Validates the login request data.
        - UsUsername and UsPassword must come together.
        - UsPhone can be provided alone without UsUsername and UsPassword.
        """
        ususername = data.get('UsUsername')
        uspassword = data.get('UsPassword')
        usphone = data.get('UsPhone')

        # Case 1: If UsPhone is provided, UsUsername and UsPassword should not be present
        if usphone and (ususername or uspassword):
            return {'error': 'يجب كتابة إما رقم الهاتف أو اسم المستخدم وكلمة المرور معًا، وليس كلاهما'}, 400

        # Case 2: If UsUsername or UsPassword is provided, both must be provided
        if (ususername and not uspassword) or (uspassword and not ususername):
            return {'error': 'يجب كتابة كل من اسم المستخدم وكلمة المرور معًا'}, 400

        # Case 3: If UsUsername and UsPassword are both provided, validate them
        if ususername and uspassword:
            error = LoginValidator.validate_ususername(data)
            if error:
                return error

            # error = LoginValidator.validate_uspassword(data)
            # if error:
            #     return error

        # Case 4: If only UsPhone is provided, validation passes (no need to check username or password)
        if usphone:
            return None  # UsPhone is valid, so no errors

        # If neither UsPhone nor UsUsername/UsPassword are provided, return an error
        if not usphone and not ususername and not uspassword:
            return {'error': 'يجب تقديم إما رقم الهاتف أو اسم المستخدم وكلمة المرور'}, 400

        return None  # All validations passed




#-------------------------------------------------------------------------------------------------

class ChangePhoneNumberValidator:
    """
    A class to handle the validation of change phone number request fields like new_phone_number.
    """

    @staticmethod
    def check_964_phone_number(new_phone_number):
        """
        Checks the complexity of the phone number.
        - Must start with 964 and have exactly 13 digits.
        """
        # Check if new_phone_number is provided
        if not new_phone_number:
            return {'error': 'رقم الهاتف مطلوب'}, 400
        
        # Ensure the phone number starts with 964 and has exactly 13 digits
        if not new_phone_number.startswith("964") or len(new_phone_number) != 13:
            return {'error': 'يجب أن يبدأ رقم الهاتف بـ 964 ويكون مكونًا من 13 رقمًا'}, 400
        
        # Ensure it contains only digits
        if not new_phone_number.isdigit():
            return {'error': 'يجب أن يحتوي رقم الهاتف على أرقام فقط'}, 400

        return None  # No errors, valid phone number

    @staticmethod
    def validate_change_phone_number_data(data):
        """
        Validates the change phone number request data.
        """

        new_phone_number = data.get('new_phone_number')

        # Check if new_phone_number is provided
        if not new_phone_number:
            return {'error': 'يجب كتابة رقم الهاتف الجديد'}, 400

        # Validate the phone number format (starting with 964 and 13 digits)
        error = ChangePhoneNumberValidator.check_964_phone_number(new_phone_number)
        if error:
            return error

        return None  # All validations passed
    


#-------------------------------------------------------------------------------------------------

class ChangePasswordValidator:
    """
    A class to handle the validation of password change request fields like new_password.
    """

    @staticmethod
    def check_password_complexity(password):
        """
        Checks the complexity of the password.
        - At least one lowercase letter, one uppercase letter, one digit, and one special character.
        """
        if len(password) < 8:
            return "يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل"
        if not re.search(r'[A-Z]', password):
            return "يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل"
        if not re.search(r'[a-z]', password):
            return "يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل"
        if not re.search(r'[0-9]', password):
            return "يجب أن تحتوي كلمة المرور على رقم واحد على الأقل"
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return "يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل"
        return "ok"

    @staticmethod
    def validate_change_password_data(data):
        """
        Validates the change password request data.
        - Both new_password and confirm_password must be provided and match.
        - Password must meet the complexity requirements.
        """
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Ensure new_password and confirm_password are provided
        if not new_password or not confirm_password:
            return {'error': 'يجب إدخال كل من كلمة المرور الجديدة وتأكيد كلمة المرور'}, 400

        # Ensure new_password and confirm_password match
        if new_password != confirm_password:
            return {'error': 'كلمة المرور وتأكيد كلمة المرور غير متطابقتين'}, 400

        # Validate password complexity
        complexity_message = ChangePasswordValidator.check_password_complexity(new_password)
        if complexity_message != "ok":
            return {'error': complexity_message}, 400

        return None  # All validations passed
    

#-------------------------------------------------------------------------------------------------

class CreateUserValidator:
    """
    A class to handle the validation of creating a new user.
    """

    @staticmethod
    def check_password_complexity(password):
        """
        Checks the complexity of the password.
        - At least one lowercase letter, one uppercase letter, one digit, and one special character.
        """
        if len(password) < 8:
            return "يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل"
        if not re.search(r'[A-Z]', password):
            return "يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل"
        if not re.search(r'[a-z]', password):
            return "يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل"
        if not re.search(r'[0-9]', password):
            return "يجب أن تحتوي كلمة المرور على رقم واحد على الأقل"
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return "يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل"
        return "ok"

    @staticmethod
    def validate_ususername(data):
        """
        Validates the 'ususername' field.
        - Must be present in the request.
        - Must contain only English letters.
        """
        ususername = data.get('ususername')

        # Check if UsUsername is provided
        if not ususername:
            return {'error': 'اسم المستخدم مطلوب في الطلب'}, 400
        
        # # Check if UsUsername contains only English letters
        # if not re.match(r'^[A-Za-z0-9._-]+$', ususername):
        #     return {'error': 'يجب أن يحتوي اسم المستخدم على أحرف إنجليزية فقط'}, 400
        
        # Check if UsUsername contains Arabic letters
        if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', ususername):
            return {'error': 'يجب ألا يحتوي اسم المستخدم على أحرف عربية'}, 400

        return None

    @staticmethod
    def validate_uspassword(data):
        """
        Validates the 'uspassword' field.
        - Must be present in the request.
        - Must meet the complexity requirements.
        """
        uspassword = data.get('uspassword')

        # Check if UsPassword is provided
        if not uspassword:
            return {'error': 'كلمة المرور مطلوبة في الطلب'}, 400

        # Check password complexity
        complexity_message = CreateUserValidator.check_password_complexity(uspassword)
        if complexity_message != "ok":
            return {'error': complexity_message}, 400

        return None

    @staticmethod
    def validate_roles_orgid(data):
        """
        Validates the 'roles_id' and 'orgID' fields.
        - Must be present in the request.
        - roles_id must be a list.
        - orgID must be present and valid.
        """
        roles_id = data.get('roles_id')
        orgID = data.get('orgid')

        if not roles_id or not isinstance(roles_id, list) or len(roles_id) == 0:
            return {'error': 'يجب تحديد الصلاحيات'}, 400

        if not orgID:
            return {'error': 'يجب تحديد التشكيل او المجموعة'}, 400

        return None

    @staticmethod
    def validate_create_user_data(data):
        """
        Validates the entire data for creating a user.
        - Validate ususername and uspassword together.
        - Validate roles_id and orgID.
        """
        # Validate Username and Password
        ususername = data.get('ususername')
        uspassword = data.get('uspassword')

        if (ususername and not uspassword) or (uspassword and not ususername):
            return {'error': 'يجب كتابة كل من اسم المستخدم وكلمة المرور معًا'}, 400

        if ususername and uspassword:
            error = CreateUserValidator.validate_ususername(data)
            if error:
                return error

            error = CreateUserValidator.validate_uspassword(data)
            if error:
                return error

        # Validate Roles and Organization ID
        error = CreateUserValidator.validate_roles_orgid(data)
        if error:
            return error

        return None  # All validations passed

#-------------------------------------------------------------------------------------------------

class UserEditValidator:
    """
    A class to handle the validation of the user edit request.
    """

    @staticmethod
    def validate_roles_id(data):
        """
        Validates the 'roles_id' field.
        - Must be a list and must not be empty.
        """
        roles_id = data.get('roles_id', [])
        if not isinstance(roles_id, list) or len(roles_id) == 0:
            return {'error': 'يجب تحديد الصلاحيات'}, 400
        return None

    @staticmethod
    def validate_orgid_list(data):
        """
        Validates the 'orgid_list' field.
        - Must be a list and must not be empty.
        """
        orgid_list = data.get('orgid')
        if orgid_list is None:
            return {'error': 'يجب تحديد قائمة التشكيل او المجموعة'}, 400
        return None

    @staticmethod
    def validate_usisactive(data):
        """
        Validates the 'usisactive' field.
        - Must be a boolean value.
        """
        usisactive = data.get('usisactive')
        if not isinstance(usisactive, bool):
            return {'error': 'يجب أن تكون حالة النشاط (usisactive) إما True أو False'}, 400
        return None

    @staticmethod
    def validate_permissions(data):
        """
        Validates the 'user_permissions' field.
        - Must be a list and must not be empty.
        """
        permissions = data.get('user_permissions', [])
        if not isinstance(permissions, list) or len(permissions) == 0:
            return {'error': 'يجب تحديد الصلاحيات'}, 400
        return None

    @staticmethod
    def validate_record_list(data):
        """
        Validates the 'record_list' field.
        - Must be a list and can be optional.
        """
        record_list = data.get('recordid', [])
        if not isinstance(record_list, list):
            return {'error': 'يجب أن تكون recordid قائمة'}, 400
        return None

    @staticmethod
    def validate_edit_user_data(data):
        """
        Validates the entire data for editing a user.
        """

        # Validate roles_id
        error = UserEditValidator.validate_roles_id(data)
        if error:
            return error

        # Validate orgid_list
        error = UserEditValidator.validate_orgid_list(data)
        if error:
            return error

        # # Validate usisactive (must be boolean)
        # error = UserEditValidator.validate_usisactive(data)
        # if error:
        #     return error

        # # Validate record_list (optional, but must be a list if present)
        # error = UserEditValidator.validate_record_list(data)
        # if error:
        #     return error

        return None  # All validations passed




















#-------------------------------------------------------------------------------------------------

# Structure the AddUserValidator class to handle validation for the add_user API.
class AddUserValidator:
    """
    A class to handle the validation of fields for the 'add_user' API.
    """

    @staticmethod
    def validate_ususername(ususername):
        """
        Validates the 'ususername' field.
        - Must be provided.
        - Must contain only valid alphanumeric characters and allowed symbols.
        """
        if not ususername:
            return {'error': 'اسم المستخدم مطلوب'}, 400
        
        # # Check if UsUsername contains only valid alphanumeric characters and allowed symbols
        # if not re.match(r'^[A-Za-z0-9._-]+$', ususername):
        #     return {'error': 'يجب أن يحتوي اسم المستخدم على أحرف إنجليزية أو أرقام أو رموز (._-)'}, 400

        return None

    @staticmethod
    def validate_uspassword(uspassword):
        """
        Validates the 'uspassword' field.
        - Must be provided.
        - Must meet complexity requirements.
        """
        if not uspassword:
            return {'error': 'كلمة المرور مطلوبة'}, 400

        # Check password complexity
        if len(uspassword) < 8:
            return {'error': 'يجب أن تحتوي كلمة المرور على 8 أحرف على الأقل'}, 400
        if not re.search(r'[A-Z]', uspassword):
            return {'error': 'يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل'}, 400
        if not re.search(r'[a-z]', uspassword):
            return {'error': 'يجب أن تحتوي كلمة المرور على حرف صغير واحد على الأقل'}, 400
        if not re.search(r'[0-9]', uspassword):
            return {'error': 'يجب أن تحتوي كلمة المرور على رقم واحد على الأقل'}, 400
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', uspassword):
            return {'error': 'يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل'}, 400

        return None
    

    @staticmethod
    def validate_usname(name, field_name):
        """
        Validates name fields (firstname, secondname, etc.).
        - Must contain only alphabetic characters, spaces, apostrophes, or hyphens.
        """
        if not name:
            return {'error': f'الحقل {field_name} مطلوب'}, 400
        
        if not re.match(r'^[a-zA-Z\u0621-\u064A\s\'-]+$', name):  # Supports Arabic and English letters, spaces, apostrophes, hyphens
            return {'error': f'يجب أن يحتوي {field_name} على أحرف فقط'}, 400

        return None

    @staticmethod
    def validate_usbirthdate(birthdate):
        """
        Validates the 'usbirthdate' field.
        - Must be a valid date in 'YYYY-MM-DD' format.
        - Must not be in the future.
        """
        if not birthdate:
            return {'error': 'تاريخ الميلاد مطلوب'}, 400
        
        try:
            # Ensure date is in correct format
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
            
            # Check if birthdate is in the future
            if birth_date > datetime.now():
                return {'error': 'لا يمكن أن يكون تاريخ الميلاد في المستقبل'}, 400
        except ValueError:
            return {'error': 'يجب أن يكون تاريخ الميلاد بتنسيق YYYY-MM-DD'}, 400

        return None

    @staticmethod
    def validate_usgender(gender):
        """
        Validates the 'usgender' field.
        - Must be one of the predefined valid options (e.g., 'ذكر', 'انثى').
        """
        valid_genders = ['ذكر', 'انثى']  # Add more valid options if needed
        
        if not gender:
            return {'error': 'الجنس مطلوب'}, 400
        
        if gender.lower() not in valid_genders:
            return {'error': 'الجنس غير صحيح. الخيارات المتاحة هي ذكر أو انثى'}, 400

        return None


    @staticmethod
    def validate_usphoneno(usphoneno):
        """
        Validates the 'usphoneno' field.
        - Must be a valid phone number.
        """
        if not usphoneno:
            return {'error': 'رقم الهاتف مطلوب'}, 400

        # Example of a phone number validation (must contain 10-15 digits)
        if not re.match(r'^\d{10,15}$', usphoneno):
            return {'error': 'يجب أن يحتوي رقم الهاتف على 10 إلى 15 رقما'}, 400

        return None

    @staticmethod
    def validate_orgid(orgID):
        """
        Validates the 'orgid' field.
        - Must be provided and be a valid integer.
        """
        if not orgID:
            return {'error': 'رقم المجموعة مطلوب'}, 400

        if not isinstance(orgID, int):
            return {'error': 'يجب أن يكون رقم المجموعة عدد صحيح'}, 400

        return None

    @staticmethod
    def validate_add_user_data(data):
        """
        Validates the entire user data for the 'add_user' API.
        """
        # Validate UsUsername
        error = AddUserValidator.validate_ususername(data.get('ususername'))
        if error:
            return error

        # Validate UsPassword
        error = AddUserValidator.validate_uspassword(data.get('uspassword'))
        if error:
            return error

        # Validate UsPhoneNo
        error = AddUserValidator.validate_usphoneno(data.get('usphoneno'))
        if error:
            return error

        # Validate OrgID
        error = AddUserValidator.validate_orgid(data.get('orgid'))
        if error:
            return error
        
        # Validate Name fields (firstname, secondname, thirdname, forthname, surname)
        error = AddUserValidator.validate_usname(data.get('usfirstname'), 'الاسم الأول')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('ussecondname'), 'الاسم الثاني')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('usthirdname'), 'الاسم الثالث')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('usforthname'), 'الاسم الرابع')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('ussurname'), 'اللقب')
        if error:
            return error

        # Validate Birthdate
        error = AddUserValidator.validate_usbirthdate(data.get('usbirthdate'))
        if error:
            return error

        # Validate Gender
        error = AddUserValidator.validate_usgender(data.get('usgender'))
        if error:
            return error

        # If all validations pass, return None
        return None
    


#-------------------------------------------------------------------------------------------------

# Structure the AddUserValidator class to handle validation for the add_user API.
class EditUserValidator:
    """
    A class to handle the validation of fields for the 'add_user' API.
    """

    @staticmethod
    def validate_ususername(ususername):
        """
        Validates the 'ususername' field.
        - Must be provided.
        - Must contain only valid alphanumeric characters and allowed symbols.
        """
        if not ususername:
            return {'error': 'اسم المستخدم مطلوب'}, 400
        
        # # Check if UsUsername contains only valid alphanumeric characters and allowed symbols
        # if not re.match(r'^[A-Za-z0-9._-]+$', ususername):
        #     return {'error': 'يجب أن يحتوي اسم المستخدم على أحرف إنجليزية أو أرقام أو رموز (._-)'}, 400

        return None
    

    @staticmethod
    def validate_usname(name, field_name):
        """
        Validates name fields (firstname, secondname, etc.).
        - Must contain only alphabetic characters, spaces, apostrophes, or hyphens.
        """
        if not name:
            return {'error': f'الحقل {field_name} مطلوب'}, 400
        
        if not re.match(r'^[a-zA-Z\u0621-\u064A\s\'-]+$', name):  # Supports Arabic and English letters, spaces, apostrophes, hyphens
            return {'error': f'يجب أن يحتوي {field_name} على أحرف فقط'}, 400

        return None

    @staticmethod
    def validate_usbirthdate(birthdate):
        """
        Validates the 'usbirthdate' field.
        - Must be a valid date in 'YYYY-MM-DD' format.
        - Must not be in the future.
        """
        if not birthdate:
            return {'error': 'تاريخ الميلاد مطلوب'}, 400
        
        try:
            # Ensure date is in correct format
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
            
            # Check if birthdate is in the future
            if birth_date > datetime.now():
                return {'error': 'لا يمكن أن يكون تاريخ الميلاد في المستقبل'}, 400
        except ValueError:
            return {'error': 'يجب أن يكون تاريخ الميلاد بتنسيق YYYY-MM-DD'}, 400

        return None

    @staticmethod
    def validate_usgender(gender):
        """
        Validates the 'usgender' field.
        - Must be one of the predefined valid options (e.g., 'ذكر', 'انثى').
        """
        valid_genders = ['ذكر', 'انثى']  # Add more valid options if needed
        
        if not gender:
            return {'error': 'الجنس مطلوب'}, 400
        
        if gender.lower() not in valid_genders:
            return {'error': 'الجنس غير صحيح. الخيارات المتاحة هي ذكر أو انثى'}, 400

        return None


    @staticmethod
    def validate_usphoneno(usphoneno):
        """
        Validates the 'usphoneno' field.
        - Must be a valid phone number.
        """
        if not usphoneno:
            return {'error': 'رقم الهاتف مطلوب'}, 400

        # Example of a phone number validation (must contain 10-15 digits)
        if not re.match(r'^\d{10,15}$', usphoneno):
            return {'error': 'يجب أن يحتوي رقم الهاتف على 10 إلى 15 رقما'}, 400

        return None

    @staticmethod
    def validate_orgid(orgID):
        """
        Validates the 'orgid' field.
        - Must be provided and be a valid integer.
        """
        if not orgID:
            return {'error': 'رقم المجموعة مطلوب'}, 400

        if not isinstance(orgID, int):
            return {'error': 'يجب أن يكون رقم المجموعة عدد صحيح'}, 400

        return None

    @staticmethod
    def validate_add_user_data(data):
        """
        Validates the entire user data for the 'add_user' API.
        """
        # Validate UsUsername
        error = AddUserValidator.validate_ususername(data.get('ususername'))
        if error:
            return error

        # Validate UsPhoneNo
        error = AddUserValidator.validate_usphoneno(data.get('usphoneno'))
        if error:
            return error

        # Validate OrgID
        error = AddUserValidator.validate_orgid(data.get('orgid'))
        if error:
            return error
        
        # Validate Name fields (firstname, secondname, thirdname, forthname, surname)
        error = AddUserValidator.validate_usname(data.get('usfirstname'), 'الاسم الأول')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('ussecondname'), 'الاسم الثاني')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('usthirdname'), 'الاسم الثالث')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('usforthname'), 'الاسم الرابع')
        if error:
            return error

        error = AddUserValidator.validate_usname(data.get('ussurname'), 'اللقب')
        if error:
            return error

        # Validate Birthdate
        error = AddUserValidator.validate_usbirthdate(data.get('usbirthdate'))
        if error:
            return error

        # Validate Gender
        error = AddUserValidator.validate_usgender(data.get('usgender'))
        if error:
            return error

        # If all validations pass, return None
        return None
    

#-------------------------------------------------------------------------------------------------
class AddSubstrateValidator:
    """
    A class to handle the validation of fields for the Substrate API.
    """

    @staticmethod
    def validate_Elname(name, field_name, required=True):
        """
        Validates name fields (firstname, secondname, etc.).
        - Must contain only alphabetic characters, spaces, apostrophes, or hyphens.
        - If required is False, it will only validate if a value is provided.
        """
        if required and not name:
            return {'error': f'الحقل {field_name} مطلوب'}, 400
        
        if name and not re.match(r'^[a-zA-Z\u0621-\u064A\s\'-]+$', name):  # Supports Arabic and English letters, spaces, apostrophes, hyphens
            return {'error': f'يجب أن يحتوي {field_name} على أحرف فقط'}, 400

        return None
    
    @staticmethod
    def validate_Elbirthdate(birthdate):
        """
        Validates the 'usbirthdate' field.
        - Must be a valid date in 'YYYY-MM-DD' format.
        - Must not be in the future.
        """
        if not birthdate:
            return {'error': 'تاريخ الميلاد مطلوب'}, 400
        
        try:
            # Ensure date is in correct format
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
            
            # Check if birthdate is in the future
            if birth_date > datetime.now():
                return {'error': 'لا يمكن أن يكون تاريخ الميلاد في المستقبل'}, 400
        except ValueError:
            return {'error': 'يجب أن يكون تاريخ الميلاد بتنسيق YYYY-MM-DD'}, 400

        return None
    
    @staticmethod
    def validate_gender(gender):
        """
        Validates the 'usgender' field.
        - Must be one of the predefined valid options (e.g., 'ذكر', 'انثى').
        """
        valid_genders = ['ذكر', 'انثى']  # Add more valid options if needed
        
        if not gender:
            return {'error': 'الجنس مطلوب'}, 400
        
        if gender.lower() not in valid_genders:
            return {'error': 'الجنس غير صحيح. الخيارات المتاحة هي ذكر أو انثى'}, 400

        return None


    @staticmethod
    def validate_phone_number(usphoneno):
        """
        Validates the 'usphoneno' field.
        - Must be a valid phone number.
        """
        if not usphoneno:
            return {'error': 'رقم الهاتف مطلوب'}, 400

        # Example of a phone number validation (must contain 10-15 digits)
        if not re.match(r'^\d{10,15}$', usphoneno):
            return {'error': 'يجب أن يحتوي رقم الهاتف على 10 إلى 15 رقما'}, 400

        return None
    
    @staticmethod
    def validate_national_numberr(usphoneno):
        """
        Validates the 'usphoneno' field.
        - Must be a valid phone number.
        """
        if not usphoneno:
            return {'error': 'رقم الهاتف مطلوب'}, 400

        # Example of a phone number validation (must contain 10-15 digits)
        if not re.match(r'^\d{10,15}$', usphoneno):
            return {'error': 'يجب أن تحتوي رقم البطاقة الموحدة على 10 إلى 15 رقما'}, 400

        return None
    
    @staticmethod
    def validate_file(card_photo):
        """
        Validates that a file (e.g., 'card_photo') is uploaded and is of valid type.
        """
        if not card_photo:
            return {'error': 'صورة بطاقة الناخب مطلوبة'}, 400

        # Check if the file has a valid extension (you can modify this as needed)
        valid_extensions = ['.png', '.jpg', '.jpeg', '.pdf']
        if not card_photo.filename.lower().endswith(tuple(valid_extensions)):
            return {'error': 'يجب أن تكون الصورة بتنسيق PNG أو JPG أو JPEG أو pdf'}, 400

        return None



    @staticmethod
    def validate_request_data(data, files):
        """
        Validates the entire request data.
        This method now accepts both `data` (form data) and `files` (file uploads).
        """
        # Validate name fields (assuming all names are required except for optional fields)
        name_fields = [
            ('name', 'الاسم الأول', True),  # Required
            ('father_name', 'اسم الأب', True),  # Required
            ('third_name', 'الاسم الثالث', True),  # Required
            ('forth_name', 'الاسم الرابع', False),  # Optional
            ('surn_ame', 'اللقب', False)  # Optional
        ]
        
        # Loop through and validate name fields
        for field_key, field_label, required in name_fields:
            error = AddSubstrateValidator.validate_Elname(data.get(field_key), field_label, required)
            if error:
                return error

        # Validate other fields like birthdate, national_number, phone_number, etc.
        error = AddSubstrateValidator.validate_Elbirthdate(data.get('birth_date'))
        if error:
            return error

        error = AddSubstrateValidator.validate_national_numberr(data.get('national_number'))
        if error:
            return error

        error = AddSubstrateValidator.validate_phone_number(data.get('phone_number'))
        if error:
            return error

        error = AddSubstrateValidator.validate_gender(data.get('gender'))
        if error:
            return error

        # Validate file upload (card photo)
        error = AddSubstrateValidator.validate_file(files.get('card_photo'))
        if error:
            return error

        # If all validations pass, return None
        return None



#-------------------------------------------------------------------------------------------------
class EditSubstrateValidator:
    """
    A class to handle the validation of fields for the Substrate API.
    """

    @staticmethod
    def validate_Elname(name, field_name, required=True):
        """
        Validates name fields (firstname, secondname, etc.).
        - Must contain only alphabetic characters, spaces, apostrophes, or hyphens.
        - If required is False, it will only validate if a value is provided.
        """
        if required and not name:
            return {'error': f'الحقل {field_name} مطلوب'}, 400
        
        if name and not re.match(r'^[a-zA-Z\u0621-\u064A\s\'-]+$', name):  # Supports Arabic and English letters, spaces, apostrophes, hyphens
            return {'error': f'يجب أن يحتوي {field_name} على أحرف فقط'}, 400

        return None
    
    @staticmethod
    def validate_Elbirthdate(birthdate):
        """
        Validates the 'usbirthdate' field.
        - Must be a valid date in 'YYYY-MM-DD' format.
        - Must not be in the future.
        """
        if not birthdate:
            return {'error': 'تاريخ الميلاد مطلوب'}, 400
        
        try:
            # Ensure date is in correct format
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
            
            # Check if birthdate is in the future
            if birth_date > datetime.now():
                return {'error': 'لا يمكن أن يكون تاريخ الميلاد في المستقبل'}, 400
        except ValueError:
            return {'error': 'يجب أن يكون تاريخ الميلاد بتنسيق YYYY-MM-DD'}, 400

        return None
    
    @staticmethod
    def validate_gender(gender):
        """
        Validates the 'usgender' field.
        - Must be one of the predefined valid options (e.g., 'ذكر', 'انثى').
        """
        valid_genders = ['ذكر', 'انثى']  # Add more valid options if needed
        
        if not gender:
            return {'error': 'الجنس مطلوب'}, 400
        
        if gender.lower() not in valid_genders:
            return {'error': 'الجنس غير صحيح. الخيارات المتاحة هي ذكر أو انثى'}, 400

        return None


    @staticmethod
    def validate_phone_number(usphoneno):
        """
        Validates the 'usphoneno' field.
        - Must be a valid phone number.
        """
        if not usphoneno:
            return {'error': 'رقم الهاتف مطلوب'}, 400

        # Example of a phone number validation (must contain 10-15 digits)
        if not re.match(r'^\d{10,15}$', usphoneno):
            return {'error': 'يجب أن يحتوي رقم الهاتف على 10 إلى 15 رقما'}, 400

        return None
    
    @staticmethod
    def validate_national_numberr(usphoneno):
        """
        Validates the 'usphoneno' field.
        - Must be a valid phone number.
        """
        if not usphoneno:
            return {'error': 'رقم الهاتف مطلوب'}, 400

        # Example of a phone number validation (must contain 10-15 digits)
        if not re.match(r'^\d{10,15}$', usphoneno):
            return {'error': 'يجب أن تحتوي رقم البطاقة الموحدة على 10 إلى 15 رقما'}, 400

        return None
    
    @staticmethod
    def validate_file(card_photo):
        """
        Validates that a file (e.g., 'card_photo') is uploaded and is of valid type.
        """
        if not card_photo:
            return {'error': 'صورة بطاقة الناخب مطلوبة'}, 400

        # Check if the file has a valid extension (you can modify this as needed)
        valid_extensions = ['.png', '.jpg', '.jpeg', '.pdf']
        if not card_photo.filename.lower().endswith(tuple(valid_extensions)):
            return {'error': 'يجب أن تكون الصورة بتنسيق PNG أو JPG أو JPEG أو pdf'}, 400

        return None



    @staticmethod
    def validate_request_data(data, files):
        """
        Validates the entire request data.
        This method now accepts both `data` (form data) and `files` (file uploads).
        """
        # Validate name fields (assuming all names are required except for optional fields)
        name_fields = [
            ('name', 'الاسم الأول', True),  # Required
            ('father_name', 'اسم الأب', True),  # Required
            ('third_name', 'الاسم الثالث', True),  # Required
            ('forth_name', 'الاسم الرابع', False),  # Optional
            ('surn_ame', 'اللقب', False)  # Optional
        ]
        
        # Loop through and validate name fields
        for field_key, field_label, required in name_fields:
            error = EditSubstrateValidator.validate_Elname(data.get(field_key), field_label, required)
            if error:
                return error

        # Validate other fields like birthdate, national_number, phone_number, etc.
        error = EditSubstrateValidator.validate_Elbirthdate(data.get('birth_date'))
        if error:
            return error

        error = EditSubstrateValidator.validate_national_numberr(data.get('national_number'))
        if error:
            return error

        error = EditSubstrateValidator.validate_phone_number(data.get('phone_number'))
        if error:
            return error

        error = EditSubstrateValidator.validate_gender(data.get('gender'))
        if error:
            return error

        # Validate file upload (card photo)
        # error = EditSubstrateValidator.validate_file(files.get('card_photo'))
        # if error:
        #     return error

        # If all validations pass, return None
        return None

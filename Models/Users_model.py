from exts import db
import datetime

class usertable(db.Model):
    usid = db.Column(db.BigInteger, primary_key=True)
    usfirstname = db.Column(db.Unicode(25), nullable=True)
    ussecondname = db.Column(db.Unicode(25), nullable=True)
    usthirdname = db.Column(db.Unicode(25), nullable=True)
    uslastname = db.Column(db.Unicode(25), nullable=True)
    ususername = db.Column(db.Unicode(50), nullable=True, unique=True)
    uspassword = db.Column(db.Text(), nullable=True)
    usphoneno = db.Column(db.String(20), nullable=True)
    usemail = db.Column(db.String(80), nullable=True)
    usisonline = db.Column(db.Boolean(), nullable=True, default=False)  
    usonoffdate = db.Column(db.DateTime, nullable=True)
    ususerempno = db.Column(db.BigInteger, nullable=True)
    ususeridintno = db.Column(db.BigInteger, nullable=True)
    usisactive = db.Column(db.Boolean(), nullable=True, default=True) 
    usisdelete = db.Column(db.Boolean(), nullable=True, default=False) 
    usisfirstlogin = db.Column(db.Boolean(), nullable=True, default=True) 
    timestamp = db.Column(db.DateTime(), nullable=True)
    urid = db.Column(db.BigInteger, nullable=True)
    uraccesstoken = db.Column(db.Text(), nullable=True)
    user_try = db.Column(db.Integer, nullable=True, default='0')



    def __repr__(self):
        """
        returns string rep of object

        """
        return f"<user {self.ususername}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, usisactive):
        # self.UsFirstName = UsFirstName
        # self.UsSecondName = UsSecondName
        # self.UsThirdName = UsThirdName
        # self.UsLastName = UsLastName
        # self.UsUsername = UsUsername
        # self.UsPassword = UsPassword
        # self.UsPhoneNo = UsPhoneNo
        # self.UsEmail = UsEmail
        # self.UsUserEmpNo = UsUserEmpNo
        # self.UsUserIdintNo = UsUserIdintNo 
        # self.UsIsDelete = UsIsDelete
        self.usisactive = usisactive 
        # self.ur_id = ur_id
        # self.ur_access_token = ur_access_token
        db.session.commit()

######################################################################################
# Database Models
# Role model

class role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    isactive = db.Column(db.Boolean(), nullable=False)
    isdelete = db.Column(db.Boolean(), nullable=False)
    createdtime = db.Column(db.DateTime, nullable=False)
    updatestime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """
        returns string rep of object

        """
        return f"<role {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):

        db.session.delete(self)
        db.session.commit()


######################################################################################
# Database Models
# Role-User model

class roleuser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.BigInteger(), nullable=False)
    roleid = db.Column(db.BigInteger(), nullable=False)
    orgid = db.Column(db.BigInteger(), nullable=False)
    isactive = db.Column(db.Boolean(), nullable=False)
    isdelete = db.Column(db.Boolean(), nullable=False)
    createdtime = db.Column(db.DateTime, nullable=False)
    updatestime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """
        returns string rep of object

        """
        return f"<roleuser {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):

        db.session.delete(self)
        db.session.commit()


######################################################################################
# Database Models
# Privileges model

class privileges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    createdtime = db.Column(db.DateTime, nullable=False)
    updatestime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """
        returns string rep of object

        """
        return f"<privileges {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):

        db.session.delete(self)
        db.session.commit()


######################################################################################
# Database Models
# Role-Privilege model

class roleprivilege(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roleid = db.Column(db.BigInteger(), nullable=False)
    privilegeid = db.Column(db.BigInteger(), nullable=False)
    createdtime = db.Column(db.DateTime, nullable=False)
    updatestime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """
        returns string rep of object

        """
        return f"<roleprivilege {self.id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):

        db.session.delete(self)
        db.session.commit()


######################################################################################
class accesstoken(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    token = db.Column(db.Text(), nullable=True)
    expirationdate = db.Column(db.DateTime, nullable=True)


    def __repr__(self):
        return f"<accesstoken {self.token} >"
    
    def save(self):
        """
        The save function is used to save the changes made to a model instance.
        It takes in no arguments and returns nothing.
        """
        db.session.add(self)
        db.session.commit()



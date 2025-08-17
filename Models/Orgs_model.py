from exts import db
from datetime import datetime

class orgs(db.Model):
    # __table_args__ = {'extend_existing': True}
    orgid = db.Column(db.Integer, primary_key=True)
    orgup = db.Column(db.Integer(), nullable=False)
    orglevel = db.Column(db.Integer(), nullable=False)
    orgenname = db.Column(db.Text(), nullable=True)
    orgarname = db.Column(db.Unicode(255), nullable=False)
    orgtype = db.Column(db.Unicode(255), nullable=True)
    orgnumber = db.Column(db.Integer(), nullable=True)
    orgcreated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    orgisactive = db.Column(db.Boolean(), nullable=False)
    isdelete = db.Column(db.Boolean(), nullable=True, default=False) 

    def __repr__(self):

        return f"<orgid {self.orgarname}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # def update(self, OrgID, OrgUp, OrgLevel, OrgEnName, OrgArName, OrgKuName, OrgIsActive):
    #     self.OrgID = OrgID
    #     self.OrgUp = OrgUp
    #     self.OrgLevel = OrgLevel
    #     self.OrgEnName = OrgEnName
    #     self.OrgArName = OrgArName
    #     self.OrgKuName = OrgKuName
    #     self.OrgIsActive = OrgIsActive
    #     db.session.commit()

######################################################################################
# Database Models
# LogActions model
class logactions(db.Model):
    logid = db.Column(db.BigInteger, primary_key=True)
    usid = db.Column(db.Integer(), nullable=True) 
    orgid = db.Column(db.Integer(), nullable=True) 
    methodname = db.Column(db.Unicode(255), nullable=True)
    parameters = db.Column(db.Unicode(), nullable=True)
    tablename = db.Column(db.String(150), nullable=True)
    extraproperties = db.Column(db.Text(), nullable=True)
    apiurl = db.Column(db.Unicode(), nullable=True)
    jsondata = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    def __repr__(self):
        """
        returns string rep of object

        """
        return f"<logactions {self.methodname}>"

    def save(self):
        db.session.add(self)
        db.session.commit()



#######################################################################################
class qr_codedata(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    q_code_id = db.Column(db.Text(), nullable=True)
    qr_code_json = db.Column(db.Text(), nullable=False, default='')
    time_stamp = db.Column(db.DateTime, nullable=False)
    urid = db.Column(db.BigInteger, nullable=True)

    def __repr__(self):
      
        return f"<qr_codedata {self.q_code_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()




#################################################################################
# class groups(db.Model):
#     # __table_args__ = {'extend_existing': True}
#     group_id = db.Column(db.Integer, primary_key=True)
#     group_up = db.Column(db.Integer(), nullable=False)
#     group_level = db.Column(db.Integer(), nullable=False)
#     group_name = db.Column(db.Text(), nullable=True)
#     group_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     group_isactive = db.Column(db.Boolean(), nullable=False)
#     group_isdelete = db.Column(db.Boolean(), nullable=True, default=False) 

#     def __repr__(self):

#         return f"<group_id {self.group_name}>"

#     def save(self):
#         db.session.add(self)
#         db.session.commit()

#     def delete(self):
#         db.session.delete(self)
#         db.session.commit()

##################################################################################


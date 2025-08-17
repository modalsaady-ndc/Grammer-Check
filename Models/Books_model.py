from exts import db
from datetime import datetime


############################################################################################################
# الكتاب الاصلي
class books(db.Model):
    # __table_args__ = {'extend_existing': True}
    book_id = db.Column(db.BigInteger, primary_key=True)
    incoming_number = db.Column(db.Integer(), nullable=False) # رقم الوارد
    outcoming_number = db.Column(db.Integer(), nullable=True) # رقم الصادر
    organization_date = db.Column(db.Date, nullable=True, default=lambda: datetime.utcnow().date())  # تاريخ التنظيم (date only)
    section = db.Column(db.Text(), nullable=False) # القسم
    to = db.Column(db.Unicode(500), nullable=False) # الى/
    subject = db.Column(db.Unicode(500), nullable=True) # الموضوع
    form = db.Column(db.Text(), nullable=True)  # النموذج
    specification_approve = db.Column(db.Text(), nullable=True) # المواصفاة المعتمدة
    evaluation = db.Column(db.Text(), nullable=True) # التقييم
    description = db.Column(db.Text(), nullable=False) # الوصف
    notes = db.Column(db.Text(), nullable=False) # الملاحظات
    attachments_text = db.Column(db.Text(), nullable=True) # المرفقات كنص
    attachments_id = db.Column(db.Integer(), nullable=True) # المرفقات
    copy_to = db.Column(db.Text(), nullable=False) # صورة عنه الى/
    physical_path = db.Column(db.Text(), nullable=True) # نسخة من الكتاب لعد التوقيع
    time_stamp = db.Column(db.DateTime(), nullable=True)
    hash_book_id = db.Column(db.Text(), nullable=True) # نسخة من الكتاب المشفر
    pre_hash_id = db.Column(db.Text(), nullable=True) # الحاق بالكتاب الاصلي ان وجد
    is_active = db.Column(db.Boolean(), nullable=True, default=True)
    is_delete = db.Column(db.Boolean(), nullable=True, default=False) 

    def __repr__(self):

        return f"<books {self.book_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


############################################################################################################
# جدول المرفقات
class attachments(db.Model):
    # __table_args__ = {'extend_existing': True}
    attach_id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.Integer(), nullable=False) # الكتاب الاصلي
    physical_path = db.Column(db.Text(), nullable=False) # نسخة من الكتاب بعد التوقيع
    attachments_text = db.Column(db.Text(), nullable=True) # المرفقات كنص
    time_stamp = db.Column(db.DateTime(), nullable=True)
    hash_attach_id = db.Column(db.Text(), nullable=False) # نسخة من المرفقات المشفر
    is_active = db.Column(db.Boolean(), nullable=True, default=False)
    is_active = db.Column(db.Boolean(), nullable=True, default=False)
    is_delete = db.Column(db.Boolean(), nullable=True, default=False) 

    def __repr__(self):

        return f"<attachments {self.attach_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()




############################################################################################################
# جدول ارسال الكتب
class transfer_book(db.Model):
    # __table_args__ = {'extend_existing': True}
    trans_id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.Integer(), nullable=False) # الكتاب الاصلي
    org_send_id = db.Column(db.Integer(), nullable=False) # الجهة المرسلة
    org_recieve_id = db.Column(db.Integer(), nullable=False) # الجهة المستلمة
    notes = db.Column(db.Text(), nullable=True) # الملاحظات
    time_stamp = db.Column(db.DateTime(), nullable=True)
    hash_trans_id = db.Column(db.Text(), nullable=True) # نسخة من الارسال المشفر
    is_send = db.Column(db.Boolean(), nullable=True, default=False)
    is_seen = db.Column(db.Boolean(), nullable=True, default=False)
    is_download = db.Column(db.Boolean(), nullable=True, default=False)
    is_active = db.Column(db.Boolean(), nullable=True, default=False)
    is_delete = db.Column(db.Boolean(), nullable=True, default=False) 

    def __repr__(self):

        return f"<transfer_book {self.trans_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
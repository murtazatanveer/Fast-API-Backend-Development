from Configuration.supabaseClient import Base
from sqlalchemy import Column , String , Boolean , DateTime , Float
from sqlalchemy.sql import func

from Utils.genUid import generateUid

class UserModel(Base):
    __tablename__="users"
    uid=Column(String(36),primary_key=True,default=generateUid,index=True)
    fullName=Column(String(50), nullable=False)
    username=Column(String(50),nullable=False,unique=True,index=True)
    email=Column(String(255),unique=True,nullable=False,index=True)
    isMarried=Column(Boolean,default=True,nullable=True)
    height=Column(Float,nullable=True)
    weight=Column(Float,nullable=True)

    createdAt = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )



import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.user import User
from app.models.doctor import Doctor


async def check_doctors():
    db = AsyncSessionLocal()
    result = await db.execute(
        select(User, Doctor).join(Doctor, User.id == Doctor.user_id)
    )
    users = result.all()
    print("\nDoctors in database:")
    for u in users:
        print(f"Email: {u.User.email}, Doctor ID: {u.Doctor.id}, Name: {u.Doctor.full_name}")
    await db.close()


if __name__ == "__main__":
    asyncio.run(check_doctors())

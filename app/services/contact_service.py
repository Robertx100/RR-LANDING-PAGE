from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import ContactSubmission

async def save_contact_submission(db: AsyncSession, data: dict):
    # Business logic: Check if email already exists
    query = select(ContactSubmission).filter(ContactSubmission.email == data['email'])
    result = await db.execute(query)
    if result.scalars().first():
        raise ValueError("Email already submitted.")

    new_submission = ContactSubmission(**data)
    db.add(new_submission)
    await db.commit()
    await db.refresh(new_submission)
    return new_submission

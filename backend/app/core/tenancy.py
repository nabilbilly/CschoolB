from fastapi import Header, HTTPException

def get_school_id(x_school_id: str = Header(...)):
    if not x_school_id:
        raise HTTPException(status_code=400, detail="X-School-ID header missing")
    return x_school_id

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from api.schemas.match import MatchResponse
from api.services.match_service import evaluate_resume_job_match

router = APIRouter(prefix="/match", tags=["Resume Match"])


@router.post("/", response_model=MatchResponse)
async def match_resume_to_job(
    job_description: str = Form(""),
    file: UploadFile | None = File(None),
):
    try:
        return await evaluate_resume_job_match(
            job_description=job_description,
            file=file,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to evaluate resume–job match",
        )

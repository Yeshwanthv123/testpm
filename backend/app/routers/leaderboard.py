from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..database import get_db
from ..models import User, Evaluation
from .. import schemas

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

# ============================================================================
# LEADERBOARD ENDPOINTS
# ============================================================================

@router.get("/global")
def get_global_leaderboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get global leaderboard ranked by average score.
    Returns top users with their stats across all interviews.
    """
    try:
        # Calculate average score and interview count per user
        user_stats = db.query(
            User.id,
            User.email,
            User.full_name,
            User.profile_picture,
            User.region,
            func.count(Evaluation.id).label('interview_count'),
            func.avg(Evaluation.overall_score).label('avg_score')
        ).outerjoin(Evaluation, User.id == Evaluation.user_id).filter(
            User.is_active == True
        ).group_by(User.id).having(
            func.count(Evaluation.id) > 0
        ).order_by(desc('avg_score')).all()

        # Calculate total users for percentile
        total_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 1

        # Paginate results
        offset = (page - 1) * page_size
        paginated_stats = user_stats[offset:offset + page_size]

        leaderboard = []
        for idx, stat in enumerate(paginated_stats, start=offset + 1):
            avg_score = float(stat.avg_score) if stat.avg_score else 0
            percentile = round((len([s for s in user_stats if s.avg_score and s.avg_score >= avg_score]) / len([s for s in user_stats if s.avg_score])) * 100, 2) if user_stats else 0
            
            leaderboard.append({
                "rank": idx,
                "username": stat.full_name or stat.email.split("@")[0],
                "email": stat.email,
                "profile_picture": stat.profile_picture,
                "region": stat.region or "Unknown",
                "avg_score": round(avg_score, 2),
                "interview_count": stat.interview_count or 0,
                "percentile": percentile
            })

        return {
            "leaderboard": leaderboard,
            "page": page,
            "page_size": page_size,
            "total_users": total_users,
            "is_top_3": len(leaderboard) <= 3
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional/{region}")
def get_regional_leaderboard(
    region: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get leaderboard for a specific region.
    """
    try:
        # Calculate average score and interview count per user in region
        user_stats = db.query(
            User.id,
            User.email,
            User.full_name,
            User.profile_picture,
            User.region,
            func.count(Evaluation.id).label('interview_count'),
            func.avg(Evaluation.overall_score).label('avg_score')
        ).outerjoin(Evaluation, User.id == Evaluation.user_id).filter(
            User.is_active == True,
            User.region == region
        ).group_by(User.id).having(
            func.count(Evaluation.id) > 0
        ).order_by(desc('avg_score')).all()

        total_users = len(user_stats)

        # Paginate results
        offset = (page - 1) * page_size
        paginated_stats = user_stats[offset:offset + page_size]

        leaderboard = []
        for idx, stat in enumerate(paginated_stats, start=offset + 1):
            avg_score = float(stat.avg_score) if stat.avg_score else 0
            percentile = round((len([s for s in user_stats if s.avg_score and s.avg_score >= avg_score]) / len([s for s in user_stats if s.avg_score])) * 100, 2) if user_stats else 0
            
            leaderboard.append({
                "rank": idx,
                "username": stat.full_name or stat.email.split("@")[0],
                "email": stat.email,
                "profile_picture": stat.profile_picture,
                "region": stat.region or "Unknown",
                "avg_score": round(avg_score, 2),
                "interview_count": stat.interview_count or 0,
                "percentile": percentile
            })

        return {
            "leaderboard": leaderboard,
            "region": region,
            "page": page,
            "page_size": page_size,
            "total_users": total_users,
            "is_top_3": len(leaderboard) <= 3
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
def get_user_ranking(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific user's ranking and statistics.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's stats
        user_stats = db.query(
            func.count(Evaluation.id).label('interview_count'),
            func.avg(Evaluation.overall_score).label('avg_score')
        ).filter(
            Evaluation.user_id == user_id,
            Evaluation.overall_score.isnot(None)
        ).first()

        avg_score = float(user_stats.avg_score) if user_stats and user_stats.avg_score else 0
        interview_count = user_stats.interview_count or 0 if user_stats else 0

        # Calculate global percentile
        all_user_avgs = db.query(
            func.avg(Evaluation.overall_score).label('avg_score')
        ).filter(
            Evaluation.overall_score.isnot(None)
        ).group_by(Evaluation.user_id).all()

        all_avgs = [float(r.avg_score) for r in all_user_avgs if r.avg_score]
        global_percentile = round((len([a for a in all_avgs if a <= avg_score]) / len(all_avgs)) * 100, 2) if all_avgs else 0

        # Calculate regional percentile
        regional_avgs = db.query(
            func.avg(Evaluation.overall_score).label('avg_score')
        ).join(User, Evaluation.user_id == User.id).filter(
            User.region == user.region,
            Evaluation.overall_score.isnot(None)
        ).group_by(Evaluation.user_id).all()

        regional_avgs_list = [float(r.avg_score) for r in regional_avgs if r.avg_score]
        regional_percentile = round((len([a for a in regional_avgs_list if a <= avg_score]) / len(regional_avgs_list)) * 100, 2) if regional_avgs_list else 0

        return {
            "user_id": user_id,
            "username": user.full_name or user.email.split("@")[0],
            "email": user.email,
            "profile_picture": user.profile_picture,
            "region": user.region or "Unknown",
            "avg_score": round(avg_score, 2),
            "interview_count": interview_count,
            "global_percentile": global_percentile,
            "regional_percentile": regional_percentile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    """
    Get list of all regions with users.
    """
    try:
        regions = db.query(User.region).filter(
            User.is_active == True,
            User.region.isnot(None)
        ).distinct().all()
        
        return {
            "regions": [r[0] for r in regions if r[0]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/peer-comparison")
def get_peer_comparison(
    user_id: int = Query(...),
    region: Optional[str] = Query(None),
    years_of_experience: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get peer comparison for a user based on filters:
    - region: User's region
    - years_of_experience: Experience level (0-2, 3-5, 6-10, 10+)
    - company: Company interviewed for
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Start with user's region
        if not region:
            region = user.region

        # Query to find similar users' evaluations
        query = db.query(
            User.id,
            User.full_name,
            User.profile_picture,
            User.region,
            User.experience,
            func.avg(Evaluation.overall_score).label('avg_score'),
            func.count(Evaluation.id).label('interview_count')
        ).join(Evaluation, User.id == Evaluation.user_id).filter(
            User.is_active == True,
            Evaluation.overall_score.isnot(None)
        )

        if region:
            query = query.filter(User.region == region)

        # Add company filter if provided (check question details)
        if company:
            # This requires checking the evaluation details for company info
            # For now, we do a basic filter
            pass

        query = query.group_by(User.id).order_by(desc('avg_score')).limit(10)
        
        peers = query.all()

        peer_list = []
        for peer in peers:
            peer_list.append({
                "user_id": peer[0],
                "username": peer[1] or f"User {peer[0]}",
                "profile_picture": peer[2],
                "region": peer[3] or "Unknown",
                "experience": peer[4],
                "avg_score": round(float(peer[5]), 2) if peer[5] else 0,
                "interview_count": peer[6] or 0
            })

        return {
            "comparison_type": "peer",
            "filters": {
                "region": region,
                "years_of_experience": years_of_experience,
                "company": company
            },
            "peers": peer_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

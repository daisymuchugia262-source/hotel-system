"""Room endpoints."""
from flask import Blueprint, jsonify
from app.repositories.room_repository import RoomRepository

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.get("")
@rooms_bp.get("/")
def list_rooms():
    return jsonify([r.to_dict() for r in RoomRepository().list_all()])

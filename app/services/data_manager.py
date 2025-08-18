import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict

class DataManager:
    """
    A centralized data management system for AI agents.
    """
    def __init__(self):
        self.profile_data = None
        self.calendar_data = None
        self.task_data = None
        print("✅ DataManager initialized.")


    def load_data(self, profile_json: str, calendar_json: str, task_json: str):
        """Loads and parses JSON data sources."""
        self.profile_data = json.loads(profile_json)
        self.calendar_data = json.loads(calendar_json)
        self.task_data = json.loads(task_json)
        print("✅ Profile, Calendar, and Task data loaded.")


    def get_student_profile(self, student_id: str) -> Dict:
        """Retrieves a specific student's profile."""
        if self.profile_data:
            return next((p for p in self.profile_data.get("profiles", [])
                         if p.get("id") == student_id), None)
        return None


    def _parse_datetime(self, dt_str: str) -> datetime:
        """Parses various datetime string formats into a UTC datetime object."""
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.astimezone(timezone.utc)
        except ValueError:
            dt = datetime.fromisoformat(dt_str)
            return dt.replace(tzinfo=timezone.utc)


    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """Filters and retrieves upcoming calendar events."""
        if not self.calendar_data: return []
        now = datetime.now(timezone.utc)
        future = now + timedelta(days=days)
        events = []
        for event in self.calendar_data.get("events", []):
            try:
                start_time = self._parse_datetime(event["start"]["dateTime"])
                if now <= start_time <= future:
                    events.append(event)
            except (KeyError, ValueError):
                continue
        return events


    def get_active_tasks(self) -> List[Dict]:
        """Retrieves and filters active, non-completed tasks."""
        if not self.task_data: return []
        now = datetime.now(timezone.utc)
        active_tasks = []
        for task in self.task_data.get("tasks", []):
            try:
                due_date = self._parse_datetime(task["due"])
                if task.get("status") == "needsAction" and due_date > now:
                    task["due_datetime"] = due_date
                    active_tasks.append(task)
            except (KeyError, ValueError):
                continue
        return active_tasks


# ==============================================================================
# ✅ TEST BLOCK (UPDATED)
# This test now mocks the current date to ensure it always passes.
# To test this file, run `python -m app.services.data_manager` from the root directory.
# ==============================================================================
if __name__ == "__main__":
    from pathlib import Path
    from unittest.mock import patch

    def main():
        """Main function to test the DataManager."""
        print("\n--- Running DataManager Test ---")

        # Mock the current time to be a specific date in 2025
        # This ensures the date-based functions work correctly.
        mock_now = datetime(2025, 8, 18, 10, 0, 0, tzinfo=timezone.utc)

        with patch('app.services.data_manager.datetime') as mock_date:
            mock_date.now.return_value = mock_now
            mock_date.fromisoformat.side_effect = lambda *args, **kwargs: datetime.fromisoformat(*args, **kwargs)

            try:
                # 1. Initialize the DataManager
                data_manager = DataManager()

                # 2. Load data from the /data directory
                print("\n[1. Loading JSON data...]")
                data_path = Path(__file__).parent.parent.parent / "data"

                profile_file = data_path / "profile.json"
                calendar_file = data_path / "calendar.json"
                task_file = data_path / "tasks.json"

                if not all([f.exists() for f in [profile_file, calendar_file, task_file]]):
                    print("❌ Error: One or more data files not found in the 'data' directory.")
                    return

                with open(profile_file, "r") as f: profile_json = f.read()
                with open(calendar_file, "r") as f: calendar_json = f.read()
                with open(task_file, "r") as f: task_json = f.read()

                data_manager.load_data(profile_json, calendar_json, task_json)

                # 3. Test the getter methods
                print("\n[2. Testing getter methods...]")

                # Test get_student_profile
                profile = data_manager.get_student_profile("student_123")
                assert profile is not None, "Profile for student_123 should be found."
                print(f"   -> Found profile for: {profile.get('personal_info', {}).get('name', 'N/A')}")

                # Test get_upcoming_events
                events = data_manager.get_upcoming_events()
                assert len(events) > 0, "Should find at least one upcoming event."
                print(f"   -> Found {len(events)} upcoming event(s) in the next 7 days.")
                print(f"      - First upcoming event: {events[0]['summary']}")

                # Test get_active_tasks
                tasks = data_manager.get_active_tasks()
                assert len(tasks) > 0, "Should find at least one active task."
                print(f"   -> Found {len(tasks)} active task(s).")
                print(f"      - First active task: {tasks[0]['title']}")

                print("\n✅ DataManager test passed!")

            except Exception as e:
                print(f"\n❌ A critical error occurred during the test: {e}")
                import traceback
                traceback.print_exc()

    # Run the main test function
    main()
    
"""Basic smoke tests for spec-driven-mcp functionality."""
import sqlite3
import tempfile
import os
from pathlib import Path
import sys

# Add the spec_mcp module to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from spec_mcp import db


def test_basic_workflow():
    """Test the basic workflow: create feature, create spec, record verification."""
    # Use a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Override the database path for testing
        original_path = str(db.DB_PATH)
        db.DB_PATH = Path(temp_db_path)
        db._conn = db._connect()  # Reconnect to new path
        
        # Ensure schema
        db.ensure_schema(reset=True)
        
        # Test feature creation
        feature = db.create_feature("test-feature", "Test Feature")
        assert feature["feature_key"] == "test-feature"
        assert feature["name"] == "Test Feature"
        assert feature["status"] == "UNTESTED"
        
        # Test requirement creation
        req = db.create_spec("REQ-001", "test-feature", "REQUIREMENT", "System shall do something")
        assert req["id"] == "REQ-001"
        assert req["kind"] == "REQUIREMENT"
        assert req["status"] == "UNTESTED"
        
        # Test AC creation
        ac = db.create_spec("AC-001", "test-feature", "AC", "User can do X", "REQ-001")
        assert ac["id"] == "AC-001"
        assert ac["kind"] == "AC"
        assert ac["parent_id"] == "REQ-001"
        
        # Test verification
        result = db.record_event("AC-001", "PASSED", "test", "Test passed")
        assert result is not None
        
        # Check that status updated
        updated_ac = db.get_spec("AC-001")
        assert updated_ac["status"] == "VERIFIED"
        
        # Check that requirement rolled up
        updated_req = db.get_spec("REQ-001") 
        assert updated_req["status"] == "VERIFIED"
        
        # Check that feature rolled up
        updated_feature = db.get_feature("test-feature")
        assert updated_feature["status"] == "VERIFIED"
        
        print("✅ All basic workflow tests passed!")
        
    finally:
        # Clean up
        db.DB_PATH = Path(original_path)
        db._conn.close()  # Close connection before deleting
        db._conn = db._connect()  # Reconnect to original path
        try:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
        except (PermissionError, OSError):
            # Windows sometimes locks the file, ignore cleanup errors
            pass


def test_search_functionality():
    """Test search functionality."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        original_path = str(db.DB_PATH)
        db.DB_PATH = Path(temp_db_path)
        db._conn = db._connect()
        
        db.ensure_schema(reset=True)
        
        # Create test data
        db.create_feature("search-test", "Search Test Feature")
        db.create_spec("REQ-SEARCH-001", "search-test", "REQUIREMENT", "Search requirement")
        db.create_spec("AC-SEARCH-001", "search-test", "AC", "Search AC", "REQ-SEARCH-001")
        
        # Test search by kind
        reqs = db.search_specs(kind="REQUIREMENT")
        assert len(reqs) == 1
        assert reqs[0]["id"] == "REQ-SEARCH-001"
        
        acs = db.search_specs(kind="AC")
        assert len(acs) == 1
        assert acs[0]["id"] == "AC-SEARCH-001"
        
        # Test search by feature
        feature_specs = db.search_specs(feature="search-test")
        assert len(feature_specs) == 2
        
        print("✅ All search tests passed!")
        
    finally:
        db.DB_PATH = Path(original_path)
        db._conn.close()
        db._conn = db._connect()
        try:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
        except (PermissionError, OSError):
            pass


if __name__ == "__main__":
    test_basic_workflow()
    test_search_functionality()
    print("\n🎉 All tests passed! The application is working correctly.")

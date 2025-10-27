"""
Unit tests for courses.py helper functions
"""
import pytest
import sys
import os

# Add parent directory to path to import courses module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from courses import get_lesson, get_next_lesson, get_course, get_module, COURSES


class TestGetLesson:
    """Tests for get_lesson function"""
    
    def test_get_lesson_exists(self):
        """Test that get_lesson returns a valid lesson when it exists"""
        # Test getting first lesson of first course
        lesson = get_lesson(1, 1, 1)
        assert lesson is not None
        assert "title" in lesson
        assert "content" in lesson
        assert lesson["title"] == "What is Cybersecurity?"
        
        # Test getting another lesson
        lesson2 = get_lesson(2, 1, 1)
        assert lesson2 is not None
        assert lesson2["title"] == "Password Strength Secrets"
    
    def test_get_lesson_not_exists(self):
        """Test that get_lesson returns None for non-existent lessons"""
        # Non-existent course
        assert get_lesson(999, 1, 1) is None
        
        # Non-existent module
        assert get_lesson(1, 999, 1) is None
        
        # Non-existent lesson
        assert get_lesson(1, 1, 999) is None


class TestGetNextLesson:
    """Tests for get_next_lesson function"""
    
    def test_get_next_lesson_in_module(self):
        """Test get_next_lesson returns the next lesson in the same module"""
        # Course 1, Module 1, Lesson 1 -> should go to Lesson 2
        next_lesson = get_next_lesson(1, 1, 1)
        assert next_lesson is not None
        assert next_lesson == (1, 1, 2)
        
        # Verify the next lesson exists
        lesson = get_lesson(*next_lesson)
        assert lesson is not None
        assert lesson["title"] == "Common Cyber Threats"
    
    def test_get_next_lesson_next_module_or_course(self):
        """Test get_next_lesson moves to next module or course when needed"""
        # Course 1, Module 1, Lesson 3 (last lesson in module) -> should go to next module or course
        next_lesson = get_next_lesson(1, 1, 3)
        # Since Course 1 only has Module 1, it should move to Course 2, Module 1, Lesson 1
        assert next_lesson is not None
        assert next_lesson == (2, 1, 1)
        
        # Verify the next lesson exists
        lesson = get_lesson(*next_lesson)
        assert lesson is not None
        assert lesson["title"] == "Password Strength Secrets"
    
    def test_get_next_lesson_end_of_content(self):
        """Test get_next_lesson returns None when at the end of all content"""
        # Find the last course, module, and lesson
        last_course_id = max(COURSES.keys())
        last_course = COURSES[last_course_id]
        last_module_id = max(last_course["modules"].keys())
        last_module = last_course["modules"][last_module_id]
        last_lesson_id = max(last_module["lessons"].keys())
        
        # Get next lesson after the last one should return None
        next_lesson = get_next_lesson(last_course_id, last_module_id, last_lesson_id)
        assert next_lesson is None
    
    def test_get_next_lesson_invalid_input(self):
        """Test get_next_lesson handles invalid input gracefully"""
        # Non-existent course
        assert get_next_lesson(999, 1, 1) is None


class TestCourseHelpers:
    """Tests for other course helper functions"""
    
    def test_get_course(self):
        """Test get_course returns valid course data"""
        course = get_course(1)
        assert course is not None
        assert course["title"] == "🛡️ Cybersecurity Fundamentals"
        assert "modules" in course
        
    def test_get_module(self):
        """Test get_module returns valid module data"""
        module = get_module(1, 1)
        assert module is not None
        assert module["title"] == "Introduction to Cybersecurity"
        assert "lessons" in module


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

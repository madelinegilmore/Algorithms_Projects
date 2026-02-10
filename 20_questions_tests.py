import unittest
from unittest.mock import patch, mock_open, MagicMock
import io
import sys
import math
from contextlib import redirect_stdout
from search_tree import TreeNode, ObjectGuesser


# used LLM to generate test cases

class TestTreeNode(unittest.TestCase):
    """Tests for the TreeNode class"""
    
    def test_node_initialization(self):
        """Test that TreeNode initializes with correct values"""
        # Test question node
        question_node = TreeNode(question="Is it red?")
        self.assertEqual(question_node.question, "Is it red?")
        self.assertIsNone(question_node.object_name)
        self.assertIsNone(question_node.left)
        self.assertIsNone(question_node.right)
        
        # Test object node
        object_node = TreeNode(object_name="apple")
        self.assertEqual(object_node.object_name, "apple")
        self.assertIsNone(object_node.question)
        self.assertIsNone(object_node.left)
        self.assertIsNone(object_node.right)

class TestObjectGuesser(unittest.TestCase):
    """Tests for the ObjectGuesser class"""
    
    def setUp(self):
        """Set up test data"""
        # Mock CSV data for testing
        self.csv_data = "object,red,round,sweet\napple,1,1,1\nbanana,0,0,1\ntomato,1,1,0\nlemon,0,1,0"
        # Mock the open function when reading the CSV
        with patch('builtins.open', mock_open(read_data=self.csv_data)):
            self.guesser = ObjectGuesser("fake_path.csv")
    
    def test_load_data(self):
        """Test data loading from CSV"""
        # Check that features were properly loaded
        self.assertEqual(self.guesser.features, ["red", "round", "sweet"])
        
        # Check that objects were properly loaded
        self.assertEqual(len(self.guesser.data), 4)
        self.assertTrue("apple" in self.guesser.data)
        self.assertTrue("banana" in self.guesser.data)
        self.assertTrue("tomato" in self.guesser.data)
        self.assertTrue("lemon" in self.guesser.data)
        
        # Check feature values for one object
        self.assertEqual(self.guesser.data["apple"]["red"], 1)
        self.assertEqual(self.guesser.data["apple"]["round"], 1)
        self.assertEqual(self.guesser.data["apple"]["sweet"], 1)
        
        # Check feature values for another object
        self.assertEqual(self.guesser.data["banana"]["red"], 0)
        self.assertEqual(self.guesser.data["banana"]["round"], 0)
        self.assertEqual(self.guesser.data["banana"]["sweet"], 1)
    
    def test_entropy(self):
        """Test entropy calculation function"""
        # Equal split (maximum entropy)
        self.assertAlmostEqual(self.guesser._entropy(5, 5), 1.0)
        
        # All one class (minimum entropy)
        self.assertEqual(self.guesser._entropy(10, 0), 0.0)
        self.assertEqual(self.guesser._entropy(0, 10), 0.0)
        
        # Uneven split
        self.assertAlmostEqual(self.guesser._entropy(3, 7), -(3/10) * math.log2(3/10) - (7/10) * math.log2(7/10))
        
        # Handle zero total
        self.assertEqual(self.guesser._entropy(0, 0), 0.0)
    
    def test_information_gain(self):
        """Test information gain calculation"""
        # For the 'red' feature: apple and tomato are red (1), banana and lemon are not (0)
        gain = self.guesser._information_gain(["apple", "banana", "tomato", "lemon"], "red")
        
        # Calculate expected gain manually
        # Original entropy: perfect split => 1.0
        # After split: two groups of 2 => perfect split in each => 0
        # Expected gain = 1.0 - 0 = 1.0
        self.assertAlmostEqual(gain, 1.0)
        
        # 'sweet' feature: apple and banana are sweet (1), tomato and lemon are not (0)
        gain = self.guesser._information_gain(["apple", "banana", "tomato", "lemon"], "sweet")
        # perfect split => gain should be 1.0
        self.assertAlmostEqual(gain, 1.0)
        
        # 'round' feature: apple, tomato, and lemon are round (1), banana is not (0)
        gain = self.guesser._information_gain(["apple", "banana", "tomato", "lemon"], "round")
        # Split is 3:1, less balanced => gain should be less than 1.0
        self.assertLess(gain, 1.0)
    
    def test_build_tree_single_object(self):
        """Test tree building with a single object"""
        tree = self.guesser._build_tree(["apple"], self.guesser.features)
        self.assertIsNotNone(tree)
        self.assertEqual(tree.object_name, "apple")
        self.assertIsNone(tree.question)
    
    def test_build_tree_multiple_objects(self):
        """Test tree building with multiple objects"""
        tree = self.guesser._build_tree(["apple", "banana", "tomato", "lemon"], self.guesser.features)
        
        # The root should be a question node, not an object node
        self.assertIsNotNone(tree)
        self.assertIsNotNone(tree.question)  # Should be a question node
        self.assertIsNone(tree.object_name)  # Not an object node
        
        # Check that the tree has children
        self.assertIsNotNone(tree.left)
        self.assertIsNotNone(tree.right)
    
    def test_build_tree_identical_objects(self):
        """Test tree building with objects that have identical features"""
        # Create mock data with two identical objects
        with patch.object(self.guesser, 'data', {
            "obj1": {"feature1": 1, "feature2": 0},
            "obj2": {"feature1": 1, "feature2": 0}
        }):
            with patch.object(self.guesser, 'features', ["feature1", "feature2"]):
                tree = self.guesser._build_tree(["obj1", "obj2"], ["feature1", "feature2"])
                
                # After using all features, should have a leaf with both objects
                self.assertTrue(hasattr(tree, 'question') or hasattr(tree, 'object_name'))
                
                # Navigate to the leaf node
                node = tree
                while node.question:
                    if node.question == "feature1":
                        node = node.left  # Both objects have feature1=1
                    elif node.question == "feature2":
                        node = node.right  # Both objects have feature2=0
                
                # Should contain both objects in alphabetical order
                self.assertIn("obj1", node.object_name)
                self.assertIn("obj2", node.object_name)
    
    def test_should_guess_single_object(self):
        """Test should_guess with a single object remaining"""
        # With only one object, should always guess
        self.assertTrue(self.guesser._should_guess(["apple"], ["red", "round"], 10))
    
    def test_should_guess_no_features(self):
        """Test should_guess with no features remaining"""
        # With no features left, should always guess
        self.assertTrue(self.guesser._should_guess(["apple", "banana"], [], 10))
    
    def test_should_guess_few_questions_many_objects(self):
        """Test should_guess with few questions but many objects"""
        # Only 2 questions left but 5 objects - should guess
        self.assertTrue(self.guesser._should_guess(
            ["obj1", "obj2", "obj3", "obj4", "obj5"], 
            ["feature1", "feature2"], 
            2
        ))
    
    @patch('builtins.input', side_effect=['yes', 'yes', 'no', 'yes'])
    def test_play_game_correct_guess(self, mock_input):
        """Test play_game with a correct guess"""
        # Create a simple tree for testing
        with patch.object(self.guesser, '_build_tree') as mock_build_tree:
            # Create a tree: root -> left (apple) / right (banana)
            root = TreeNode(question="red")
            root.left = TreeNode(object_name="apple")
            root.right = TreeNode(object_name="banana")
            mock_build_tree.return_value = root
            
            # Capture stdout to check output
            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                self.guesser.play_game()
            
            output = captured_output.getvalue()
            self.assertIn("I guessed it!", output)
    
    @patch('builtins.input', side_effect=['no', 'no'])
    def test_play_game_incorrect_guess(self, mock_input):
        """Test play_game with an incorrect guess"""
        # Create a simple tree for testing
        with patch.object(self.guesser, '_build_tree') as mock_build_tree:
            # Create a tree: root -> left (apple) / right (banana)
            root = TreeNode(question="red")
            root.left = TreeNode(object_name="apple")
            root.right = TreeNode(object_name="banana")
            mock_build_tree.return_value = root
            
            # Capture stdout to check output
            captured_output = io.StringIO()
            with redirect_stdout(captured_output):
                self.guesser.play_game()
            
            output = captured_output.getvalue()
            self.assertIn("I couldn't guess your object correctly", output)
    
    @patch('builtins.input', side_effect=['yes', 'no', 'yes'])
    def test_play_game_multiple_objects_in_leaf(self, mock_input):
        """Test play_game with multiple objects in a leaf node"""
        # Mock a tree with a leaf containing multiple objects
        with patch.object(self.guesser, '_build_tree') as mock_build_tree:
            # Use a feature name that exists in self.guesser.features
            feature_name = self.guesser.features[0]  # Use the first feature from real features
            
            root = TreeNode(question=feature_name)
            root.left = TreeNode(object_name="apple,banana,cherry")  # Multiple objects
            root.right = TreeNode(object_name="date")
            mock_build_tree.return_value = root
            
            # Reset remaining_features for this test to include our feature
            with patch.object(self.guesser, 'features', [feature_name]):
                # Capture stdout to check output
                captured_output = io.StringIO()
                with redirect_stdout(captured_output):
                    self.guesser.play_game()
            
            # Should have guessed "banana" correctly after rejecting "apple"
            output = captured_output.getvalue()
            self.assertIn("I guessed it!", output)

if __name__ == '__main__':
    unittest.main()
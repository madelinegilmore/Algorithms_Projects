import math
import csv
from collections import defaultdict

class TreeNode:
    def __init__(self, question=None, object_name=None):
        self.question = question    
        self.object_name = object_name  
        self.left = None          
        self.right = None        

class ObjectGuesser:
    def __init__(self, csv_path):
        self.data, self.features = self._load_data(csv_path)
    
    def _load_data(self, csv_path):
        """Loads data from CSV and returns (data_dict, features_list)"""
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            features = headers[1:]
            data = {row[0]: {f: int(row[i+1]) for i, f in enumerate(features)} 
                   for row in reader}
        return data, features
    
    def _entropy(self, yes_count, no_count):
        """Calculates entropy for a yes/no split"""
        total = yes_count + no_count
        if total == 0 or yes_count == 0 or no_count == 0:
            return 0
        p_yes = yes_count / total
        p_no = no_count / total
        return -p_yes * math.log2(p_yes) - p_no * math.log2(p_no)
    
    def _information_gain(self, objects, feature):
        """Calculates how much a feature splits the data"""
        yes = [obj for obj in objects if self.data[obj][feature] == 1]
        no = [obj for obj in objects if self.data[obj][feature] == 0]
        
        # Original entropy
        total_entropy = self._entropy(len(yes), len(no))
        
        # Weighted entropy after split
        weight_yes = len(yes) / len(objects)
        weight_no = len(no) / len(objects)
        gain = total_entropy - (
            weight_yes * self._entropy(len(yes), 0) + 
            weight_no * self._entropy(0, len(no))
        )
        return gain
    
    def _build_tree(self, objects, features):
        """Recursively builds the decision tree"""
        if not objects:
            return None

        objects = sorted(objects)  # Ensure consistent alphabetical order
        
        # create a leaf node with an object if we have exactly one 
        if len(objects) == 1:
            return TreeNode(object_name=objects[0])
        
        # If no more features but multiple objects, create a node with all objects
        if not features and len(objects) > 1:
            # Store all objects in alphabetical order
            return TreeNode(object_name=",".join(objects))
        
        # Find feature with maximum information gain
        best_feature = max(features, key=lambda f: self._information_gain(objects, f))
        
        # Split objects
        yes_objects = [obj for obj in objects if self.data[obj][best_feature] == 1]
        no_objects = [obj for obj in objects if self.data[obj][best_feature] == 0]
        
        # Remove used feature
        remaining_features = [f for f in features if f != best_feature]
        
        node = TreeNode(question=best_feature)
        node.left = self._build_tree(yes_objects, remaining_features)
        node.right = self._build_tree(no_objects, remaining_features)
        
        return node
    
    #determines if its better to guess an object or ask a question
    def _should_guess(self, remaining_objects, remaining_features, questions_left):
        """Determines if we should start guessing or continue asking questions"""
        # If only one object, always guess
        if len(remaining_objects) == 1:
            return True
            
        # If no features left to distinguish objects, start guessing
        if not remaining_features:
            return True
            
        # If not enough questions left to distinguish all objects, start guessing
        # (We need at least log2(n) questions to distinguish n objects)
        if questions_left < math.log2(len(remaining_objects)):
            return True
            
        # Calculate best possible reduction in objects from asking another question
        best_split = 0
        for feature in remaining_features:
            yes_count = sum(1 for obj in remaining_objects if self.data[obj][feature] == 1)
            no_count = len(remaining_objects) - yes_count
            best_split = max(best_split, min(yes_count, no_count))
        
        # If best question eliminates less than half the objects and we have few enough 
        # objects that direct guessing would be faster, guess now
        if best_split > len(remaining_objects) / 2 and len(remaining_objects) <= questions_left:
            return True
            
        return False
    
    def play_game(self):
        """Starts a new guessing game with optimal guessing strategy"""
        print("Think of an object within the dataset, and I'll try to guess it!")
        tree = self._build_tree(list(self.data.keys()), self.features)
        
        questions_asked = 0
        max_questions = 20
        
        # Track current state
        remaining_objects = list(self.data.keys())
        remaining_features = self.features.copy()
        
        # Start at the root
        node = tree
        
        while questions_asked < max_questions:
            # If we're at a leaf node or should start guessing
            if node.object_name or self._should_guess(remaining_objects, remaining_features, max_questions - questions_asked):
                # If we have a specific object node
                if node.object_name and "," not in node.object_name:
                    answer = input(f"Is it a {node.object_name}? (yes/no) ").lower()
                    questions_asked += 1
                    
                    if answer == 'yes':
                        print("I guessed it!")
                        return
                    else:
                        print("I couldn't guess your object correctly.")
                        if questions_asked >= max_questions:
                            print("I've reached my limit of 20 questions!")
                        return
                else:
                    # Get the list of objects to guess
                    objects_to_guess = node.object_name.split(",") if node.object_name else sorted(remaining_objects)
                    
                    for obj in objects_to_guess:
                        if questions_asked >= max_questions:
                            print("I've reached my limit of 20 questions!")
                            return
                            
                        answer = input(f"Is it a {obj}? (yes/no) ").lower()
                        questions_asked += 1
                        
                        if answer == 'yes':
                            print("I guessed it!")
                            return
                    
                    print("I couldn't guess your object within 20 questions.")
                    return
            
            # Ask a question to navigate the tree
            answer = input(f"{node.question}? (yes/no) ").lower()
            questions_asked += 1
            
            # Update remaining features
            remaining_features.remove(node.question)
            
            # Update remaining objects based on answer
            if answer == 'yes':
                remaining_objects = [obj for obj in remaining_objects if self.data[obj][node.question] == 1]
                node = node.left
            else:
                remaining_objects = [obj for obj in remaining_objects if self.data[obj][node.question] == 0]
                node = node.right
        
        print("I've reached my limit of 20 questions and couldn't guess your object!")


def main(dataset_path):
    guesser = ObjectGuesser(dataset_path) 
    while True:
        guesser.play_game()
        if input("Play again? (yes/no) ").lower() != 'yes':
            break

main("/home/full_data.txt")
#!/usr/bin/env python3

from token_tree_generator import TokenDecode, Node, convert_to_node

# Create a sample tree structure for testing
def create_sample_tree():
    """Create a sample tree for testing the animation"""
    # Tree structure: (key, prob, children)
    tree_data = (
        "START", 1.0, [
            ("The", 0.7, [
                ("cat", 0.8, [
                    ("sat", 0.6, [
                        ("on", 0.9, [
                            ("the", 0.8, [
                                ("sofa", 0.7, [])
                            ])
                        ])
                    ]),
                    ("is", 0.4, [
                        ("brown", 0.6, [
                            ("in", 0.8, [
                                ("color", 0.9, [])
                            ])
                        ]),
                        ("hungry", 0.4, [
                            ("for", 0.7, [
                                ("fish", 0.8, [])
                            ])
                        ])
                    ])
                ]),
                ("dog", 0.2, [
                    ("ran", 0.7, [
                        ("quickly", 0.8, [])
                    ])
                ])
            ]),
            ("A", 0.3, [
                ("bird", 0.6, [
                    ("flew", 0.9, [
                        ("away", 0.8, [])
                    ])
                ])
            ])
        ]
    )
    
    return convert_to_node(tree_data)

if __name__ == "__main__":
    # Create the tree
    tree = create_sample_tree()
    
    # Create and render the scene
    scene = TokenDecode(tree=tree)
    
    print("Tree structure created successfully!")
    print("To render the animation, run:")
    print("manim test_animation.py TokenDecode")

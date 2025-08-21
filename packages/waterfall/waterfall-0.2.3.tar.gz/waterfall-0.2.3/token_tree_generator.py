from manim import *
import random
import numpy as np

def convert_to_node(tree):
    """Recursively convert a (key, value, children) nested list tree 
    to a Node-based tree.
    """
    key, val, children = tree
    node_children = [convert_to_node(c) for c in children]
    return Node(key, val, node_children)

class Node:
    def __init__(self, key, prob, children=None):
        self.key = key
        self.prob = prob
        self.children = children or []

m, c = -0.012892119897959181, -0.9999984801020411

class TokenDecode(Scene):
    def __init__(self, tree=None, font_size=12, **kwargs):
        self.tree = tree
        self.font_size = font_size
        self.relative_size = (font_size / -m + c) / 1860
        super().__init__(**kwargs)

    def construct(self):
        if self.tree is None:
            raise ValueError("No tree provided")

        root = self.tree
        selected_tokens = []
        current_sentence_mob = None

        def get_chains(node):
            rows = []
            for c in node.children:
                chain = ""
                child = c
                while child.children:
                    best = max(child.children, key=lambda x: x.prob or 0)
                    chain += "" + best.key
                    child = best
                rows.append((c.key, c.prob, chain.strip(), c.children))
            return rows

        current_sentence_mob = None
        y_pos_offset = self.relative_size * 0.6
        left_margin = Text("0.00", font_size=self.font_size).get_width()
        while root.children:
            rows = get_chains(root)
            if not rows:
                break
                
            # Calculate current sentence position
            current_sentence = "".join(selected_tokens) if selected_tokens else ""

            # Phase 1: Show rows with probabilities and greyed chains
            row_mobs = []
            prob_mobs = []
            
            # First pass: calculate positions to align chains
            max_tok_x_end = 0
            row_data = []
            
            for i, (tok, p, chain, _) in enumerate(rows):
                # Position calculations
                y_pos = 1 - i * y_pos_offset

                # Create sentence prefix if exists
                if current_sentence:
                    prefix_mob = Text(current_sentence + "", color=WHITE, font_size=self.font_size, should_center=False)
                    prefix_mob.set_fill(opacity=0)  # Make it transparent for positioning only
                    prefix_mob.to_edge(LEFT).shift(UP * y_pos)
                    prefix_x_end = prefix_mob.get_right()[0]
                else:
                    prefix_mob = None
                    prefix_x_end = config.frame_x_radius * -1 + left_margin + 0.15

                # Create probability text (left-aligned after prefix)
                prob_mob = Text(f"{p:.2f}", color=WHITE, font_size=self.font_size, should_center=False)
                y_offset = (m * self.font_size + c - prob_mob.get_center()[1])
                prob_mob.next_to(np.array([prefix_x_end, y_pos, 0]), RIGHT, buff=-left_margin)
                prob_mob.shift(DOWN * y_offset)
                prob_x_end = prob_mob.get_right()[0]

                # Create token text
                tok_mob = Text(tok, color=WHITE, font_size=self.font_size, should_center=False)
                if len(tok_mob) > 0:
                    y_offset = (m * self.font_size + c - tok_mob.get_center()[1])
                tok_mob.next_to(np.array([prob_x_end, y_pos, 0]), RIGHT, buff=self.relative_size * 0.2)
                if len(tok_mob) > 0:
                    tok_mob.shift(DOWN * y_offset)
                tok_x_end = tok_mob.get_right()[0]
                
                max_tok_x_end = max(max_tok_x_end, tok_x_end)
                row_data.append((y_pos, prefix_mob, prob_mob, tok_mob, chain))
            
            # Second pass: create chains aligned to the same x position
            for i, (y_pos, prefix_mob, prob_mob, tok_mob, chain) in enumerate(row_data):
                # Create chain text (greyed out) - all chains start at the same x position
                if chain:
                    chain_mob = Text(chain, color=GREY, font_size=self.font_size, should_center=False)
                    y_offset = (m * self.font_size + c - chain_mob.get_center()[1])
                    chain_mob.next_to(np.array([max_tok_x_end, y_pos, 0]), RIGHT, buff=self.relative_size * 0.2)
                    # Align chain vertically with the token (bottom alignment)
                    # chain_mob.align_to(tok_mob, DOWN)
                    chain_mob.shift(DOWN * y_offset)
                else:
                    chain_mob = None

                # Update row_data to include chain_mob for later reference
                row_data[i] = (y_pos, prefix_mob, prob_mob, tok_mob, chain, chain_mob)

                # Collect all parts for this row
                row_parts = [prob_mob, tok_mob]
                if prefix_mob:
                    row_parts.insert(0, prefix_mob)
                if chain_mob:
                    row_parts.append(chain_mob)
                
                row_group = VGroup(*row_parts)
                self.add(row_group)
                row_mobs.append(row_group)
                prob_mobs.append(prob_mob)

            self.wait(0.15)

            # Phase 2: Fade out old probabilities, fade in new blue probabilities
            new_probs = [max(min(p + random.uniform(-0.1, 0.1), 1), 0) for (_, p, _, _) in rows]
            new_prob_mobs = []
            
            # Create new probability texts
            for i, new_p in enumerate(new_probs):
                new_prob_mob = Text(f"{new_p:.2f}", color=BLUE, font_size=self.font_size, should_center=False)
                new_prob_mob.move_to(prob_mobs[i].get_center())
                new_prob_mobs.append(new_prob_mob)

            # Animate probability change
            fade_out_anims = [FadeOut(prob_mob) for prob_mob in prob_mobs]
            fade_in_anims = [FadeIn(new_prob_mob) for new_prob_mob in new_prob_mobs]
            
            self.play(*fade_out_anims, run_time=0.15)
            self.play(*fade_in_anims, run_time=0.15)
            
            # Update row_mobs with new probability texts
            new_row_mobs = []
            for i, (y_pos, prefix_mob, old_prob_mob, tok_mob, chain, chain_mob) in enumerate(row_data):
                # Create new row with updated probability
                new_row_parts = [new_prob_mobs[i], tok_mob]
                if prefix_mob:
                    new_row_parts.insert(0, prefix_mob)
                if chain_mob:
                    new_row_parts.append(chain_mob)
                
                new_row_group = VGroup(*new_row_parts)
                new_row_mobs.append(new_row_group)
            
            # Replace the old row_mobs with new ones
            row_mobs = new_row_mobs
            prob_mobs = new_prob_mobs
            
            self.wait(0.15)

            # Phase 3: Select one row based on new probabilities
            idx = random.choices(range(len(rows)), weights=new_probs)[0]
            selected_row = row_mobs[idx]
            selected_token = rows[idx][0]

            # Fade out non-selected rows
            fade_out_anims = []
            for i, row in enumerate(row_mobs):
                if i != idx:
                    fade_out_anims.append(FadeOut(row))
            
            if fade_out_anims:
                self.play(*fade_out_anims, run_time=0.15)

            # Move selected row up and fade out chain
            # target_y = 1.5
            # selected_row_copy = selected_row.copy()
            
            # Remove chain from selected row (fade it out)
            row_parts = list(selected_row)
            if len(row_parts) > 3:  # Has chain
                chain_part = row_parts[-1]
                other_parts = row_parts[:-1]
                self.play(
                    FadeOut(chain_part),
                    VGroup(*other_parts).animate.shift(UP * (idx * y_offset + 1)),
                    run_time=0.8
                )
            else:
                self.play(selected_row.animate.shift(UP * (idx * y_offset + 1)), run_time=0.8)

            self.wait(0.3)

            # Phase 4: Animate token joining the sentence
            selected_tokens.append(selected_token)
            new_sentence = "".join(selected_tokens)
            
            # Create new sentence text
            new_sentence_mob = Text(new_sentence, color=WHITE, font_size=self.font_size, should_center=False)
            y_offset = (m * self.font_size + c - new_sentence_mob.get_center()[1])
            new_sentence_mob.to_edge(LEFT, buff=0.15)
            new_sentence_mob.move_to(np.array([new_sentence_mob.get_center()[0], 2.5, 0]))
            new_sentence_mob.shift(DOWN * y_offset)

            # Fade out the selected row and fade in the new sentence
            self.play(FadeOut(selected_row), run_time=0.3)
            
            self.play(FadeIn(new_sentence_mob), run_time=0.15)
            if current_sentence_mob:
                self.remove(current_sentence_mob)

            current_sentence_mob = new_sentence_mob
            self.wait(0.15)

            # Update root for next iteration
            root = Node(new_sentence, None, rows[idx][3])
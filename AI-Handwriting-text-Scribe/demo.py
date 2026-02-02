import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import logging
import numpy as np
import svgwrite
import textwrap

import drawing
from rnn import rnn


class Hand(object):

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.nn = rnn(
            log_dir=os.path.join(script_dir, 'logs'),
            checkpoint_dir=os.path.join(script_dir, 'checkpoints'),
            prediction_dir=os.path.join(script_dir, 'predictions'),
            learning_rates=[.0001, .00005, .00002],
            batch_sizes=[32, 64, 64],
            patiences=[1500, 1000, 500],
            beta1_decays=[.9, .9, .9],
            validation_batch_size=32,
            optimizer='rms',
            num_training_steps=100000,
            warm_start_init_step=17900,
            regularization_constant=0.0,
            keep_prob=1.0,
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            logging_level=logging.CRITICAL,
            grad_clip=10,
            lstm_size=400,
            output_mixture_components=20,
            attention_mixture_components=10
        )
        self.nn.restore()

    def write(
        self,
        filename,
        lines,
        biases=None,
        styles=None,
        page_width=1860,
        page_height=3508,
        margins=None,
        ruled=True
    ):
        if margins is None:
            margins = {"left": 150, "right": 150, "top": 250, "bottom": 250}

        # ================= FINAL LAYOUT SETTINGS =================
        # 1. EXACTLY 25 LINES
        LINES_PER_PAGE = 25
        
        # Calculate dynamic gap to fit exactly 25 lines in the space
        usable_height = page_height - margins["top"] - margins["bottom"]
        LINE_GAP = int(usable_height / LINES_PER_PAGE)
        
        # 2. SCALE
        # Increased gap means we need slightly bigger text to look balanced
        SCALE = 2.4 

        # 3. SPACING
        # We need to account for the wider spacing (1.30 stretch)
        # Lower divisor = fewer chars per line
        usable_width = page_width - margins["left"] - margins["right"]
        char_limit = int(usable_width / 24) 
        # =========================================================

        final_lines = []
        if isinstance(lines, str):
            final_lines = textwrap.wrap(lines, width=char_limit)
        else:
            full_text = " ".join(lines)
            final_lines = textwrap.wrap(full_text, width=char_limit)

        print(f"Layout: {len(final_lines)} lines total | {LINES_PER_PAGE} lines/page")

        total_lines = len(final_lines)
        if biases is None: biases = [0.75] * total_lines
        elif len(biases) < total_lines: biases += [biases[-1]] * (total_lines - len(biases))
        
        if styles is None: styles = [0] * total_lines
        elif len(styles) < total_lines: styles += [styles[-1]] * (total_lines - len(styles))

        generated_files = []
        for page_num, i in enumerate(range(0, total_lines, LINES_PER_PAGE)):
            chunk_lines = final_lines[i : i + LINES_PER_PAGE]
            chunk_biases = biases[i : i + LINES_PER_PAGE]
            chunk_styles = styles[i : i + LINES_PER_PAGE]
            
            page_filename = filename.replace(".svg", f"_p{page_num+1}.svg")
            
            strokes = self._sample(chunk_lines, biases=chunk_biases, styles=chunk_styles)
            
            self._draw(
                strokes, chunk_lines, page_filename,
                page_width, page_height, margins, ruled,
                LINE_GAP, SCALE
            )
            generated_files.append(page_filename)
            
        return generated_files

    def _sample(self, lines, biases=None, styles=None):
        num_samples = len(lines)
        max_tsteps = 60 * max(len(l) for l in lines)
        
        x_prime = np.zeros([num_samples, 1200, 3])
        x_prime_len = np.zeros([num_samples])
        chars = np.zeros([num_samples, 120])
        chars_len = np.zeros([num_samples])

        if styles:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            for i, (text, style) in enumerate(zip(lines, styles)):
                x_p = np.load(os.path.join(script_dir, f"styles/style-{style}-strokes.npy"))
                c_p = np.load(os.path.join(script_dir, f"styles/style-{style}-chars.npy")).tobytes().decode("utf-8")
                encoded = drawing.encode_ascii(c_p + " " + text)
                if len(encoded) > 120: encoded = encoded[:120]
                
                x_prime[i, :len(x_p)] = x_p
                x_prime_len[i] = len(x_p)
                chars[i, :len(encoded)] = encoded
                chars_len[i] = len(encoded)
        else:
            for i, text in enumerate(lines):
                encoded = drawing.encode_ascii(text)
                if len(encoded) > 120: encoded = encoded[:120]
                chars[i, :len(encoded)] = encoded
                chars_len[i] = len(encoded)

        [samples] = self.nn.session.run(
            [self.nn.sampled_sequence],
            feed_dict={
                self.nn.prime: styles is not None,
                self.nn.x_prime: x_prime,
                self.nn.x_prime_len: x_prime_len,
                self.nn.num_samples: num_samples,
                self.nn.sample_tsteps: max_tsteps,
                self.nn.c: chars,
                self.nn.c_len: chars_len,
                self.nn.bias: biases
            }
        )
        return [s[~np.all(s == 0.0, axis=1)] for s in samples]

    def _draw(self, strokes, lines, filename, width, height, margins, ruled, line_gap, scale):
        LEFT, RIGHT = margins["left"], width - margins["right"]
        TOP, BOTTOM = margins["top"], height - margins["bottom"]
        
        WRITING_AREA_WIDTH = width - margins["left"] - margins["right"]

        BASELINE_OFFSET = -15  
        
        # === INCREASED WORD SPACING ===
        # Increased from 1.15 to 1.30 to widen gaps between words
        DEFAULT_X_STRETCH = 1.30

        dwg = svgwrite.Drawing(filename, size=(width, height), viewBox=f"0 0 {width} {height}")
        dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill="white"))

        if ruled:
            # Vertical Margins
            dwg.add(dwg.line(start=(LEFT-20, 0), end=(LEFT-20, height), stroke="#DBDBDB", stroke_width=2))
            dwg.add(dwg.line(start=(RIGHT+20, 0), end=(RIGHT+20, height), stroke="#DBDBDB", stroke_width=2))
            
            # === DOUBLE HEADER LINE ===
            # The first line (TOP) is drawn twice with a small gap (Double Red)
            dwg.add(dwg.line(start=(0, TOP), end=(width, TOP), stroke="#FFB0B0", stroke_width=2))
            dwg.add(dwg.line(start=(0, TOP + 6), end=(width, TOP + 6), stroke="#FFB0B0", stroke_width=2))
            
            # The rest of the lines (Blue)
            y = TOP + line_gap
            while y < height - margins["bottom"] + 10: # +10 ensures we get the last line
                dwg.add(dwg.line(start=(0, y), end=(width, y), stroke="#AEC2D6", stroke_width=1))
                y += line_gap

        # Start writing on the first BLUE line (after the red header)
        y_cursor = TOP + line_gap

        for i, (offsets, text) in enumerate(zip(strokes, lines)):
            if not text:
                y_cursor += line_gap
                continue

            offsets = offsets.copy()
            offsets[:, :2] *= scale
            coords = drawing.offsets_to_coords(offsets)

            if len(coords) == 0: 
                y_cursor += line_gap; continue
            try:
                denoised = drawing.denoise(coords)
                if len(denoised) > 2: coords = denoised
            except: pass
            try:
                if len(coords) > 2: coords[:, :2] = drawing.align(coords[:, :2])
            except: pass

            coords[:, 1] *= -1
            coords[:, 0] -= coords[:, 0].min()
            
            # === JUSTIFY & STRETCH ===
            current_width = coords[:, 0].max()
            is_last_line = (i == len(lines) - 1)
            
            projected_width = current_width * DEFAULT_X_STRETCH
            fill_ratio = projected_width / WRITING_AREA_WIDTH
            
            # If line is > 65% full, stretch it to fill the line
            if fill_ratio > 0.65 and not is_last_line:
                final_stretch = WRITING_AREA_WIDTH / current_width
                if final_stretch > 1.8: final_stretch = 1.8
                coords[:, 0] *= final_stretch
            else:
                # Use default wide spacing
                coords[:, 0] *= DEFAULT_X_STRETCH
            # =========================
            
            coords[:, 0] += LEFT
            coords[:, 1] += y_cursor + BASELINE_OFFSET

            path = ""
            prev = 1.0
            for x, y, eos in coords:
                path += f"{'M' if prev else 'L'}{x},{y} "
                prev = eos

            dwg.add(svgwrite.path.Path(path).stroke("black", width=2.4, linecap="round").fill("none"))
            y_cursor += line_gap

        dwg.save()
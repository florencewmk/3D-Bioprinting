# Slide motion

Default for this project, requested 3 November 2026: every slide has an entrance
animation and a transition to the next slide, with content-appropriate pacing.
Navigation remains presenter controlled.

`slide-motion.js` applies gentle 620 ms crossfades and reads each slide's content
to choose its entrances. Cover/statements use 0.9–1.2 s reveals; agendas use
210 ms staggering; comparisons use 260 ms between columns; the conclusion's
numbered points use 300 ms staggering. Evidence/technical slides fade their
unaltered scientific artwork and reveal text in reading bands. No scientific
geometry, text scaling, chart values or media playback is changed.

Presenter bullets, history steps and chart timelines retain their own
controllers. The publication reveal remains six seconds and the opening
photograph retains its 18-second zoom. Reduced-motion preferences show content
immediately. Printing and editing cancel entrance animations to expose final
content. Transitions do not add automatic slide advancement.

Embed or refresh with `python3 tools/update_motion.py`. Its separate script block
survives targeted opening/chart/history updaters, and full builds embed it
automatically. For an isolated preview use `--output /absolute/path/index.html`.
Downloaded browser-edited HTML includes the motion controller.

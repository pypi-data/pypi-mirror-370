from barbariantuw import Game
from barbariantuw.core import Act, Animation, Actions, frame


def serpent():
    return {
        'idle': Animation(frames=[
            frame('stage/serpent1.gif'),
        ], actions=[
            Act(tick=1, act=Actions.stop),
        ]),
        'bite': Animation(frames=[
            frame('stage/serpent1.gif', tick=1),
            frame('stage/serpent2.gif', tick=6),
            frame('stage/serpent3.gif', tick=11),
            frame('stage/serpent4.gif', tick=16, dx=-3 * Game.scx, dy=-1 * Game.scy),
            frame('stage/serpent3.gif', tick=21),
            frame('stage/serpent2.gif', tick=26),
            frame('stage/serpent1.gif', tick=27),
        ], actions=[
            Act(tick=28, act=Actions.stop),
        ]),
    }


def serpent_rtl():
    return {
        'idle': Animation(frames=[
            frame('stage/serpent1.gif', xflip=True),
        ], actions=[
            Act(tick=1, act=Actions.stop),
        ]),
        'bite': Animation(frames=[
            frame('stage/serpent1.gif', xflip=True, tick=1),
            frame('stage/serpent2.gif', xflip=True, tick=6),
            frame('stage/serpent3.gif', xflip=True, tick=11),
            frame('stage/serpent4.gif', xflip=True, tick=16, dx=3 * Game.scx, dy=-1 * Game.scy),
            frame('stage/serpent3.gif', xflip=True, tick=21),
            frame('stage/serpent2.gif', xflip=True, tick=26),
            frame('stage/serpent1.gif', xflip=True, tick=27),
        ], actions=[
            Act(tick=28, act=Actions.stop),
        ]),
    }


def sang_decap():
    return {
        'sang_touche': Animation(frames=[
            frame('sprites/sang.gif', tick=11),
            frame('empty')
        ], actions=[
            Act(tick=12, act=Actions.kill),
        ]),
        'sang': Animation(frames=[
            # @formatter:off
            # TODO: invisible tickable sprites
            frame('empty',              tick=5),  # noqa
            frame('sprites/gicle1.gif', tick=10, dx=Game.chw, dy=0.8 * Game.chh),
            frame('sprites/gicle2.gif', tick=15, dx=Game.chw, dy=0.8 * Game.chh),
            frame('sprites/gicle3.gif', tick=20, dx=Game.chw, dy=0.8 * Game.chh),
            frame('empty',              tick=40),
            frame('sprites/gicle1.gif', tick=45, dx=3 * Game.chw, dy=(2 + 0.7) * Game.chh),
            frame('sprites/gicle2.gif', tick=50, dx=3 * Game.chw, dy=(2 + 0.7) * Game.chh),
            frame('sprites/gicle3.gif', tick=55, dx=3 * Game.chw, dy=(2 + 0.7) * Game.chh),
            frame('empty',              tick=56),
            # @formatter:on
        ], actions=[
            Act(tick=57, act=Actions.kill),
        ]),
        'sang_rtl': Animation(frames=[
            # @formatter:off
            frame('empty',              tick=5),
            frame('sprites/gicle1.gif', tick=10, dx=0.5 * Game.chw, dy=0.8 * Game.chh),
            frame('sprites/gicle2.gif', tick=15, dx=0.5 * Game.chw, dy=0.8 * Game.chh),
            frame('sprites/gicle3.gif', tick=20, dx=0.5 * Game.chw, dy=0.8 * Game.chh),
            frame('empty',              tick=40),
            frame('sprites/gicle1.gif', tick=45, dx=-1.75 * Game.chw, dy=(2 + 0.7) * Game.chh),
            frame('sprites/gicle2.gif', tick=50, dx=-1.75 * Game.chw, dy=(2 + 0.7) * Game.chh),
            frame('sprites/gicle3.gif', tick=55, dx=-1.75 * Game.chw, dy=(2 + 0.7) * Game.chh),
            frame('empty',              tick=56),
            # @formatter:om
        ], actions=[
            Act(tick=56, act=Actions.kill),
        ]),
    }


def tete_decap(subdir: str):
    return {
        'teteagauche': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tetedecap1.gif', tick=4,  dx=1.2 * Game.chw, dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', tick=8,  dx=0 * Game.chw,   dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', tick=12, dx=-1 * Game.chw,  dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', tick=16, dx=-2 * Game.chw,  dy=18 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', tick=20, dx=-3 * Game.chw,  dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', tick=24, dx=-4 * Game.chw,  dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', tick=28, dx=-5 * Game.chw,  dy=39 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', tick=32, dx=-6 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', tick=36, dx=-7 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', tick=40, dx=-8 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', tick=44, dx=-9 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', tick=48, dx=-10 * Game.chw, dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', tick=52, dx=-11 * Game.chw, dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', tick=56, dx=-12 * Game.chw, dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', tick=57, dx=-13 * Game.chw, dy=65 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=29, act=Actions.snd, snd='tete.ogg'),
            Act(tick=45, act=Actions.snd, snd='tete.ogg'),
            Act(tick=58, act=Actions.stop),
        ]),
        'teteadroite': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tetedecap1.gif', tick=4,  dx=1.4 * Game.chw, dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', tick=8,  dx=2 * Game.chw,   dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', tick=12, dx=3 * Game.chw,   dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', tick=16, dx=4 * Game.chw,   dy=18 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', tick=20, dx=5 * Game.chw,   dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', tick=24, dx=6 * Game.chw,   dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', tick=28, dx=7 * Game.chw,   dy=39 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', tick=32, dx=8 * Game.chw,   dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', tick=36, dx=9 * Game.chw,   dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', tick=40, dx=10 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', tick=44, dx=11 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', tick=48, dx=12 * Game.chw,  dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', tick=52, dx=13 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', tick=56, dx=14 * Game.chw,  dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', tick=57, dx=15 * Game.chw,  dy=65 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=29, act=Actions.snd, snd='tete.ogg'),
            Act(tick=45, act=Actions.snd, snd='tete.ogg'),
            Act(tick=58, act=Actions.stop),
        ]),
        'teteagauche_rtl': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tetedecap1.gif', xflip=True, tick=4,  dx=0.7 * Game.chw, dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', xflip=True, tick=8,  dx=0 * Game.chw,   dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', xflip=True, tick=12, dx=-1 * Game.chw,  dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', xflip=True, tick=16, dx=-2 * Game.chw,  dy=18 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', xflip=True, tick=20, dx=-3 * Game.chw,  dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', xflip=True, tick=24, dx=-4 * Game.chw,  dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', xflip=True, tick=28, dx=-5 * Game.chw,  dy=39 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', xflip=True, tick=32, dx=-6 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', xflip=True, tick=36, dx=-7 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', xflip=True, tick=40, dx=-8 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', xflip=True, tick=44, dx=-9 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', xflip=True, tick=48, dx=-10 * Game.chw, dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', xflip=True, tick=52, dx=-11 * Game.chw, dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', xflip=True, tick=56, dx=-12 * Game.chw, dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', xflip=True, tick=57, dx=-13 * Game.chw, dy=65 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=29, act=Actions.snd, snd='tete.ogg'),
            Act(tick=45, act=Actions.snd, snd='tete.ogg'),
            Act(tick=58, act=Actions.stop),
        ]),
        'teteadroite_rtl': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tetedecap1.gif', xflip=True, tick=4,  dx=1 * Game.chw,  dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', xflip=True, tick=8,  dx=2 * Game.chw,  dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', xflip=True, tick=12, dx=3 * Game.chw,  dy=11 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', xflip=True, tick=16, dx=4 * Game.chw,  dy=18 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', xflip=True, tick=20, dx=5 * Game.chw,  dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', xflip=True, tick=24, dx=6 * Game.chw,  dy=25 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', xflip=True, tick=28, dx=7 * Game.chw,  dy=39 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', xflip=True, tick=32, dx=8 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', xflip=True, tick=36, dx=9 * Game.chw,  dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap4.gif', xflip=True, tick=40, dx=10 * Game.chw, dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap5.gif', xflip=True, tick=44, dx=11 * Game.chw, dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap6.gif', xflip=True, tick=48, dx=12 * Game.chw, dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap1.gif', xflip=True, tick=52, dx=13 * Game.chw, dy=59 * Game.scy),
            frame(f'{subdir}/tetedecap2.gif', xflip=True, tick=56, dx=14 * Game.chw, dy=57 * Game.scy),
            frame(f'{subdir}/tetedecap3.gif', xflip=True, tick=57, dx=15 * Game.chw, dy=65 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=29, act=Actions.snd, snd='tete.ogg'),
            Act(tick=45, act=Actions.snd, snd='tete.ogg'),
            Act(tick=58, act=Actions.stop),
        ]),
        'football': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tetedecap3.gif', tick=4,   mv=(Game.chw, 0), dy=-2 * 0.6 * Game.chh),
            frame(f'{subdir}/tetedecap2.gif', tick=7,   mv=(Game.chw, 0), dy=-2 * 0.7 * Game.chh),
            frame(f'{subdir}/tetedecap1.gif', tick=15,  mv=(Game.chw, 0), dy=-2 * 0.9 * Game.chh),
            frame(f'{subdir}/tetedecap6.gif', tick=22,  mv=(Game.chw, 0), dy=-2 * 0.8 * Game.chh),
            frame(f'{subdir}/tetedecap5.gif', tick=30,  mv=(Game.chw, 0), dy=-2 * 0.4 * Game.chh),
            frame(f'{subdir}/tetedecap4.gif', tick=37,  mv=(Game.chw, 0)),
            frame(f'{subdir}/tetedecap3.gif', tick=45,  mv=(Game.chw, 0), dy=-2 * 0.1 * Game.chh),
            frame(f'{subdir}/tetedecap2.gif', tick=52,  mv=(Game.chw, 0), dy=-2 * 0.3 * Game.chh),
            frame(f'{subdir}/tetedecap1.gif', tick=60,  mv=(Game.chw, 0), dy=-2 * 0.5 * Game.chh),
            frame(f'{subdir}/tetedecap6.gif', tick=67,  mv=(Game.chw, 0), dy=-2 * 0.3 * Game.chh),
            frame(f'{subdir}/tetedecap5.gif', tick=75,  mv=(Game.chw, 0), dy=-2 * 0.1 * Game.chh),
            frame(f'{subdir}/tetedecap4.gif', tick=82,  mv=(Game.chw, 0)),
            frame(f'{subdir}/tetedecap3.gif', tick=90,  mv=(Game.chw, 0), dy=-2 * 0.1 * Game.chh),
            frame(f'{subdir}/tetedecap2.gif', tick=97,  mv=(Game.chw, 0), dy=-2 * 0.4 * Game.chh),
            frame(f'{subdir}/tetedecap1.gif', tick=105, mv=(Game.chw, 0), dy=-2 * 0.1 * Game.chh),
            frame(f'{subdir}/tetedecap3.gif', tick=112, mv=(Game.chw, 0)),
            # @formatter:on
        ], actions=[
            Act(tick=0, act=Actions.snd, snd='tete2.ogg'),
            Act(tick=38, act=Actions.snd, snd='tete.ogg'),
            Act(tick=83, act=Actions.snd, snd='tete.ogg'),
            Act(tick=113, act=Actions.stop),
        ]),
    }


def teteombre_decap():
    return {
        'teteagauche': Animation(frames=[
            # @formatter:off
            frame('spritesA/teteombre.gif', tick=4,  dx=1 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=8,  dx=0 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=12, dx=-1 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=16, dx=-2 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=20, dx=-3 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=24, dx=-4 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=28, dx=-5 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=32, dx=-6 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=36, dx=-7 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=40, dx=-8 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=44, dx=-9 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=48, dx=-10 * Game.chw, dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=52, dx=-11 * Game.chw, dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=56, dx=-12 * Game.chw, dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=57, dx=-13 * Game.chw, dy=71 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=58, act=Actions.stop),
        ]),
        'teteadroite': Animation(frames=[
            # @formatter:off
            frame('spritesA/teteombre.gif', tick=4,  dx=1.4 * Game.chw, dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=8,  dx=2 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=12, dx=3 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=16, dx=4 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=20, dx=5 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=24, dx=6 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=28, dx=7 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=32, dx=8 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=36, dx=9 * Game.chw,   dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=40, dx=10 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=44, dx=11 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=48, dx=12 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=52, dx=13 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=56, dx=14 * Game.chw,  dy=71 * Game.scy),
            frame('spritesA/teteombre.gif', tick=57, dx=15 * Game.chw,  dy=71 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=58, act=Actions.stop),
        ]),
        'football': Animation(frames=[
            # @formatter:off
            frame(f'spritesA/teteombre.gif', tick=4,   mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=7,   mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=15,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=22,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=30,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=37,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=45,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=52,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=60,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=67,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=75,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=82,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=90,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=97,  mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=105, mv=(Game.chw, 0)),
            frame(f'spritesA/teteombre.gif', tick=112, mv=(Game.chw, 0)),
            # @formatter:on
        ], actions=[
            Act(tick=113, act=Actions.stop),
        ]),
    }


def vie():
    return {
        'vie': Animation(frames=[
            # @formatter:off
            frame('fill', w=1,    h=10, fill=(0, 0, 0), dx=0),
            frame('fill', w=6,    h=10, fill=(0, 0, 0), dx=-5 * Game.scx),
            frame('fill', w=17,   h=10, fill=(0, 0, 0), dx=-16 * Game.scx),
            frame('fill', w=22,   h=10, fill=(0, 0, 0), dx=-21 * Game.scx),
            frame('fill', w=27.1, h=10, fill=(0, 0, 0), dx=-26.1 * Game.scx),
            frame('fill', w=38,   h=10, fill=(0, 0, 0), dx=-37 * Game.scx),
            frame('fill', w=43.1, h=10, fill=(0, 0, 0), dx=-42.1 * Game.scx),
            # @formatter:on
        ], actions=[
            Act(tick=1, act=Actions.stop),
        ]),
        'vie_rtl': Animation(frames=[
            # @formatter:off
            frame('fill', w=1,    h=10, fill=(0, 0, 0)),
            frame('fill', w=6,    h=10, fill=(0, 0, 0)),
            frame('fill', w=17,   h=10, fill=(0, 0, 0)),
            frame('fill', w=22,   h=10, fill=(0, 0, 0)),
            frame('fill', w=27.1, h=10, fill=(0, 0, 0)),
            frame('fill', w=38,   h=10, fill=(0, 0, 0)),
            frame('fill', w=43.1, h=10, fill=(0, 0, 0)),
            # @formatter:on
        ], actions=[
            Act(tick=1, act=Actions.stop),
        ]),
    }


def barb(subdir: str):
    return {
        'debout': Animation(frames=[
            frame(f'{subdir}/debout.gif', dx=4 * Game.scx, dy=18 * Game.scy),
        ]),
        'attente': Animation(frames=[
            frame(f'{subdir}/attente1.gif', tick=15, dx=4 * Game.scx,   dy=18 * Game.scy),
            frame(f'{subdir}/attente2.gif', tick=23, dx=2.1 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/attente3.gif', tick=30, dx=2.1 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/attente2.gif', tick=37, dx=2.1 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/attente1.gif', tick=50, dx=4 * Game.scx,   dy=18 * Game.scy),
        ], actions=[
            Act(tick=8, act=Actions.snd, snd='attente.ogg')
        ]),
        'avance': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/marche1.gif', tick=9,  mv=(Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche2.gif', tick=17, mv=(Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche3.gif', tick=27, mv=(Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  tick=36, mv=(Game.chw, 0), dx=4 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  tick=37,                   dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'recule': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/marche3.gif', tick=9,  mv=(-Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche2.gif', tick=18, mv=(-Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche1.gif', tick=26, mv=(-Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  tick=36, mv=(-Game.chw, 0), dx=4 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  tick=37,                    dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'saute': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/saut1.gif',  tick=13, dx=6 * Game.scx, dy=6 * Game.scy),
            frame(f'{subdir}/saut2.gif',  tick=30, dx=8 * Game.scx, dy=5 * Game.scy),
            frame(f'{subdir}/saut1.gif',  tick=40, dx=6 * Game.scx, dy=6 * Game.scy),
            frame(f'{subdir}/debout.gif', tick=47, dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=47, act=Actions.stop)
        ]),
        'assis': Animation(frames=[
            frame(f'{subdir}/assis1.gif', dx=4 * Game.scx, dy=26 * Game.scy),
            frame(f'{subdir}/assis2.gif', dx=2 * Game.scx, dy=38 * Game.scy),
        ]),
        'releve': Animation(frames=[
            frame(f'{subdir}/assis1.gif', dx=4 * Game.scx, dy=26 * Game.scy),
        ]),
        'rouladeAV': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/roulade1.gif',             tick=4,  mv=(Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade1.gif',             tick=7,  mv=(Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade1.gif',             tick=10, mv=(Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=13, mv=(Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=16, mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=19, mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=22, mv=(Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=25, mv=(Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=28, mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=30, mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=34, mv=(Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/debout.gif',               tick=40, dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=2, act=Actions.snd, snd='roule.ogg')
        ]),
        'rouladeAV-out': Animation(frames=[
            # non-movable roulade out
            # @formatter:off
            frame(f'{subdir}/roulade3.gif',             tick=16, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=19, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=22,                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=25,                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=28, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=30, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=34, dx=3 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/debout.gif',               tick=40, dx=4 * Game.scx,  dy=18 * Game.scy),
            # @formatter:on
        ]),
        'rouladeAR': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=5,  mv=(-Game.chw, 0), dx=3 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=8,  mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=11, mv=(-Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=14, mv=(-Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=17, mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=20, mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=23, mv=(-Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=26, mv=(-Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade1.gif',             tick=29, mv=(-Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade1.gif',             tick=35, mv=(-Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=2, act=Actions.snd, snd='roule.ogg')
        ]),
        'protegeH': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/marche1.gif',  tick=5, mv=(-Game.chw, 0), dx=8 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/protegeH.gif', tick=9,                                     dy=21 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=2, act=Actions.snd, snd='protege.ogg')
        ]),
        'protegeD': Animation(frames=[
            frame(f'{subdir}/protegeH.gif', tick=5, dy=21 * Game.scy),
            frame(f'{subdir}/protegeD.gif', tick=9, dy=19 * Game.scy),
        ]),
        'cou': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/protegeH.gif', tick=15,                   dy=21 * Game.scy),
            frame(f'{subdir}/cou2.gif',     tick=30, dx=-2 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/cou3.gif',     tick=46, dx=1 * Game.scx,  dy=19 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=15, act=Actions.snd, snd='epee.ogg'),
        ]),
        'devant': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/devant1.gif', tick=10, dx=4 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/devant2.gif', tick=20, dx=0 * Game.scx, dy=23 * Game.scy),
            frame(f'{subdir}/devant3.gif', tick=30, dx=6 * Game.scx, dy=23 * Game.scy),
            frame(f'{subdir}/devant2.gif', tick=46, dx=0 * Game.scx, dy=23 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=10, act=Actions.snd, snd='epee.ogg'),
        ]),
        'genou': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/genou1.gif', tick=10, dx=7 * Game.scx, dy=38 * Game.scy),
            frame(f'{subdir}/assis2.gif', tick=20, dx=2 * Game.scx, dy=38 * Game.scy),
            frame(f'{subdir}/genou3.gif', tick=30, dx=8 * Game.scx, dy=38 * Game.scy),
            frame(f'{subdir}/assis2.gif', tick=46, dx=2 * Game.scx, dy=38 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=10, act=Actions.snd, snd='epee.ogg'),
        ]),
        'araignee': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/toile1.gif', tick=8,  dx=6 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/toile2.gif', tick=15, dx=6 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/toile3.gif', tick=20, dx=6 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/toile4.gif', tick=33, dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=8, act=Actions.snd, snd='epee.ogg'),
            Act(tick=20, act=Actions.snd, snd='epee.ogg'),
        ]),
        'coupdepied': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/pied1.gif',  tick=9,  dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied2.gif',  tick=30, dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied1.gif',  tick=45, dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/debout.gif', tick=51, dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'coupdetete': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/debout.gif', tick=8,                     dx=4 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/tete1.gif',  tick=18,                    dx=4 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/tete2.gif',  tick=28, mv=(Game.chw, 0),  dx=4 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/tete1.gif',  tick=38, mv=(-Game.chw, 0), dx=4 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/debout.gif', tick=40,                    dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'decapite': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/retourne1.gif', tick=4,  mv=(Game.chw, 0), dx=2 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/retourne1.gif', tick=5,  mv=(Game.chw, 0), dx=2 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/retourne2.gif', tick=9,                    dx=5 * Game.scx,  dy=13 * Game.scy),
            frame(f'{subdir}/retourne2.gif', tick=14, mv=(Game.chw, 0), dx=5 * Game.scx,  dy=13 * Game.scy),
            frame(f'{subdir}/retourne3.gif', tick=15,                   dx=4 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/retourne3.gif', tick=19, mv=(Game.chw, 0), dx=4 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/retourne3.gif', tick=24, mv=(Game.chw, 0), dx=4 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/retourne3.gif', tick=29,                   dx=4 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/protegeH.gif',  tick=33,                                     dy=21 * Game.scy),
            frame(f'{subdir}/cou2.gif',      tick=39,                   dx=-2 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/cou3.gif',      tick=51,                   dx=1 * Game.scx,  dy=19 * Game.scy),
            frame(f'{subdir}/cou2.gif',      tick=60,                   dx=-2 * Game.scx, dy=17 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=15, act=Actions.snd, snd='decapite.ogg'),
        ]),
        'front': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/front1.gif', tick=5,  dx=-1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/front2.gif', tick=23, dx=2 * Game.scx,  dy=3 * Game.scy),
            frame(f'{subdir}/front3.gif', tick=30, dx=2 * Game.scx,  dy=18 * Game.scy),
            frame(f'{subdir}/front2.gif', tick=46, dx=2 * Game.scx,  dy=3 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=5, act=Actions.snd, snd='epee.ogg'),
        ]),
        'retourne': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/retourne1.gif', tick=5,  mv=(Game.chw, 0), dx=2 * Game.scx, dy=14 * Game.scy),
            frame(f'{subdir}/retourne2.gif', tick=10, mv=(Game.chw, 0), dx=5 * Game.scx, dy=13 * Game.scy),
            frame(f'{subdir}/retourne3.gif', tick=18, mv=(Game.chw, 0), dx=4 * Game.scx, dy=14 * Game.scy),
            # @formatter:on
        ]),
        'vainqueur': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=18,  dx=2 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=35,  dx=4 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur3.gif', xflip=True, tick=85,  dx=6 * Game.scx, dy=10.1 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=100, dx=4 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=101, dx=2 * Game.scx, dy=17 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=102, act=Actions.stop),
        ]),
        'vainqueurKO': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/retourne1.gif',              tick=15,  dx=2 * Game.scx, dy=14 * Game.scy),
            frame(f'{subdir}/retourne2.gif',              tick=23,  dx=5 * Game.scx, dy=13 * Game.scy),
            frame(f'{subdir}/retourne3.gif',              tick=30,  dx=4 * Game.scx, dy=14 * Game.scy),
            frame(f'{subdir}/debout.gif',                 tick=40,  dx=4 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche3.gif',                tick=40,  dx=8 * Game.scx, dy=18 * Game.scy),  # optional frame, see gestion on tick 35
            frame(f'{subdir}/marche3.gif',    xflip=True, tick=40,                   dy=18 * Game.scy),  # optional frame, see gestion on tick 35
            frame(f'{subdir}/debout.gif',                 tick=55,  dx=4 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/pied1.gif',                  tick=70,  dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied2.gif',                  tick=75,  dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied1.gif',                  tick=100, dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/debout.gif',                 tick=105, dx=4 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=123, dx=2 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=140, dx=4 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur3.gif', xflip=True, tick=195, dx=6 * Game.scx, dy=10.1 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=205, dx=4 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=231, dx=2 * Game.scx, dy=17 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=232, act=Actions.stop),
        ]),
        'touche1': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/touche2.gif', tick=1,                         dx=5 * Game.scx, dy=20 * Game.scy),
            frame(f'{subdir}/touche2.gif', tick=5,  mv=(-Game.chw,     0), dx=5 * Game.scx, dy=20 * Game.scy),
            frame(f'{subdir}/touche1.gif', tick=10, mv=(-2 * Game.chw, 0),                  dy=21 * Game.scy),
            frame(f'{subdir}/touche2.gif', tick=20, mv=(-Game.chw,     0), dx=5 * Game.scx, dy=20 * Game.scy),
            frame(f'{subdir}/debout.gif',  tick=21, dx=4 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'tombe1': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tombe1.gif', tick=1,                     dx=-16 * Game.scx, dy=21 * Game.scy),
            frame(f'{subdir}/tombe1.gif', tick=9,  mv=(-Game.chw, 0), dx=-16 * Game.scx, dy=21 * Game.scy),
            frame(f'{subdir}/tombe2.gif', tick=15, mv=(-Game.chw, 0), dx=-26 * Game.scx, dy=58 * Game.scy),
            frame(f'{subdir}/tombe3.gif', tick=25,                    dx=-26 * Game.scx, dy=41 * Game.scy),
            frame(f'{subdir}/debout.gif', tick=27, mv=(-Game.chw, 0), dx=4 * Game.scx,   dy=18 * Game.scy),
            # @formatter:on
        ]),
        'mort': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/assis1.gif', tick=15, dx=4 * Game.scx,   dy=26 * Game.scy),
            frame(f'{subdir}/mort2.gif',  tick=17, dx=4 * Game.scx,   dy=54 * Game.scy),
            frame(f'{subdir}/mort3.gif',  tick=18, dx=-10 * Game.scx, dy=52 * Game.scy),  # manual, see vainqueurKO
            frame(f'{subdir}/mort4.gif',  tick=19, dx=-22 * Game.scx, dy=66 * Game.scy),  # manual, see vainqueurKO
            # @formatter:on
        ], actions=[
            Act(tick=1, act=Actions.snd, snd='mortKO.ogg'),
            Act(tick=17, act=Actions.stop),
        ]),
        'mortdecap': Animation(frames=[
            frame(f'{subdir}/decap1.gif', tick=35, dx=6 * Game.scx, dy=30 * Game.scy),
            frame(f'{subdir}/decap2.gif', tick=70, dx=16 * Game.scx, dy=45 * Game.scy),
            frame(f'{subdir}/decap3.gif', tick=80, dx=16 * Game.scx, dy=53 * Game.scy),
            frame(f'{subdir}/decap4.gif', tick=82, dx=16 * Game.scx, dy=68 * Game.scy),
        ], actions=[
            Act(tick=1, act=Actions.snd, snd='mortdecap.ogg'),
            Act(tick=82, act=Actions.stop),
        ]),
        'mortgnome': Animation(frames=[
            frame(f'{subdir}/mort4.gif', tick=0, mv=(Game.chw / 12, 0)),
        ]),
        'mortdecapgnome': Animation(frames=[
            frame(f'{subdir}/decap4.gif', tick=0, mv=(Game.chw / 12, 0)),
        ]),
    }


def barb_rtl(subdir: str):
    return {
        'debout': Animation(frames=[
            frame(f'{subdir}/debout.gif', xflip=True, dy=18 * Game.scy),
        ]),
        'attente': Animation(frames=[
            frame(f'{subdir}/attente1.gif', xflip=True, tick=15,                   dy=18 * Game.scy),
            frame(f'{subdir}/attente2.gif', xflip=True, tick=23, dx=-4 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/attente3.gif', xflip=True, tick=30, dx=-4 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/attente2.gif', xflip=True, tick=37, dx=-4 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/attente1.gif', xflip=True, tick=50,                   dy=18 * Game.scy),
        ], actions=[
            Act(tick=8, act=Actions.snd, snd='attente.ogg')
        ]),
        'avance': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/marche1.gif', xflip=True, tick=9,  mv=(-Game.chw, 0), dx=6 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche2.gif', xflip=True, tick=17, mv=(-Game.chw, 0), dx=6 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche3.gif', xflip=True, tick=27, mv=(-Game.chw, 0),                  dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  xflip=True, tick=36, mv=(-Game.chw, 0), dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  xflip=True, tick=37,                    dy=18 * Game.scy),
            # @formatter:on
        ]),
        'recule': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/marche3.gif', xflip=True, tick=9,  mv=(Game.chw, 0),                  dy=18 * Game.scy),
            frame(f'{subdir}/marche2.gif', xflip=True, tick=18, mv=(Game.chw, 0), dx=6 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/marche1.gif', xflip=True, tick=26, mv=(Game.chw, 0), dx=6 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  xflip=True, tick=36, mv=(Game.chw, 0), dy=18 * Game.scy),
            frame(f'{subdir}/debout.gif',  xflip=True, tick=37,                   dy=18 * Game.scy),
            # @formatter:on
        ]),
        'saute': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/saut1.gif',  xflip=True, tick=13, dx=-4 * Game.scx, dy=6 * Game.scy),
            frame(f'{subdir}/saut2.gif',  xflip=True, tick=30, dx=-8 * Game.scx, dy=5 * Game.scy),
            frame(f'{subdir}/saut1.gif',  xflip=True, tick=40, dx=-5 * Game.scx, dy=6 * Game.scy),
            frame(f'{subdir}/debout.gif', xflip=True, tick=47,                   dy=18 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=47, act=Actions.stop)
        ]),
        'assis': Animation(frames=[
            frame(f'{subdir}/assis1.gif', xflip=True, dy=26 * Game.scy),
            frame(f'{subdir}/assis2.gif', xflip=True, dy=38 * Game.scy),
        ]),
        'releve': Animation(frames=[
            frame(f'{subdir}/assis1.gif', xflip=True, dy=26 * Game.scy),
        ]),
        'rouladeAV': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=4,  mv=(-Game.chw, 0), dx=3 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=7,  mv=(-Game.chw, 0), dx=3 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=10, mv=(-Game.chw, 0), dx=3 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=13, mv=(-Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=16, mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=19, mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=22, mv=(-Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=25, mv=(-Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=28, mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=30, mv=(-Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade1.gif',             tick=34, mv=(-Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/debout.gif',   xflip=True, tick=40, dy=18 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=2, act=Actions.snd, snd='roule.ogg')
        ]),
        'rouladeAV-out': Animation(frames=[
            # non-movable roulade out
            # @formatter:off
            frame(f'{subdir}/roulade3.gif',             tick=16, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=19, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=22, dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=25, dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=28, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=30, dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade1.gif',             tick=34, dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/debout.gif',   xflip=True, tick=40, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'rouladeAR': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/roulade1.gif',             tick=5,  mv=(Game.chw, 0), dx=4 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade5.gif',             tick=8,  mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=11, mv=(Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif',             tick=14, mv=(Game.chw, 0), dx=8 * Game.scx,  dy=63 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=17, mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade3.gif',             tick=20, mv=(Game.chw, 0), dx=10 * Game.scx, dy=56 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=23, mv=(Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade2.gif', xflip=True, tick=26, mv=(Game.chw, 0),                   dy=63 * Game.scy),
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=29, mv=(Game.chw, 0), dx=3 * Game.scx,  dy=38 * Game.scy),
            frame(f'{subdir}/roulade1.gif', xflip=True, tick=35, mv=(Game.chw, 0), dx=3 * Game.scx,  dy=38 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=2, act=Actions.snd, snd='roule.ogg')
        ]),
        'protegeH': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/marche1.gif',  xflip=True, tick=5, mv=(Game.chw, 0), dx=6 * Game.scx,  dy=18 * Game.scy),
            frame(f'{subdir}/protegeH.gif', xflip=True, tick=9,                                     dy=21 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=2, act=Actions.snd, snd='protege.ogg')
        ]),
        'protegeD': Animation(frames=[
            frame(f'{subdir}/protegeH.gif', xflip=True, tick=5, dy=21 * Game.scy),
            frame(f'{subdir}/protegeD.gif', xflip=True, tick=9, dy=19 * Game.scy),
        ]),
        'cou': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/protegeH.gif', xflip=True, tick=15,                    dy=21 * Game.scy),
            frame(f'{subdir}/cou2.gif',     xflip=True, tick=30,                    dy=17 * Game.scy),
            frame(f'{subdir}/cou3.gif',     xflip=True, tick=46, dx=-31 * Game.scx, dy=19 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=15, act=Actions.snd, snd='epee.ogg'),
        ]),
        'devant': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/devant1.gif', xflip=True, tick=10,                    dy=17 * Game.scy),
            frame(f'{subdir}/devant2.gif', xflip=True, tick=20,                    dy=23 * Game.scy),
            frame(f'{subdir}/devant3.gif', xflip=True, tick=30, dx=-19 * Game.scx, dy=23 * Game.scy),
            frame(f'{subdir}/devant2.gif', xflip=True, tick=46,                    dy=23 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=10, act=Actions.snd, snd='epee.ogg'),
        ]),
        'genou': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/genou1.gif', xflip=True, tick=10, dx=-2 * Game.scx, dy=38 * Game.scy),
            frame(f'{subdir}/assis2.gif', xflip=True, tick=20, dy=38 * Game.scy),
            frame(f'{subdir}/genou3.gif', xflip=True, tick=30, dx=-26 * Game.scx, dy=38 * Game.scy),
            frame(f'{subdir}/assis2.gif', xflip=True, tick=46, dy=38 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=10, act=Actions.snd, snd='epee.ogg'),
        ]),
        'araignee': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/toile1.gif', xflip=True, tick=8,  dx=-2 * Game.scx,  dy=18 * Game.scy),
            frame(f'{subdir}/toile2.gif', xflip=True, tick=15, dx=-8 * Game.scx,  dy=19 * Game.scy),
            frame(f'{subdir}/toile3.gif', xflip=True, tick=20, dx=-1 * Game.scx,  dy=18 * Game.scy),
            frame(f'{subdir}/toile4.gif', xflip=True, tick=33, dx=-21 * Game.scx, dy=18 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=8, act=Actions.snd, snd='epee.ogg'),
            Act(tick=20, act=Actions.snd, snd='epee.ogg'),
        ]),
        'coupdepied': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/pied1.gif',  xflip=True, tick=9,  dx=-3 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied2.gif',  xflip=True, tick=30, dx=-8 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied1.gif',  xflip=True, tick=45, dx=-3 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/debout.gif', xflip=True, tick=51,                   dy=18 * Game.scy),
            # @formatter:on
        ]),
        'coupdetete': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/debout.gif', xflip=True, tick=8,                                      dy=18 * Game.scy),
            frame(f'{subdir}/tete1.gif',  xflip=True, tick=18, mv=(-Game.chw, 0), dx=2 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/tete2.gif',  xflip=True, tick=28,                    dx=1 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/tete1.gif',  xflip=True, tick=38,                    dx=2 * Game.scx, dy=19 * Game.scy),
            frame(f'{subdir}/debout.gif', xflip=True, tick=40, mv=(Game.chw, 0),                   dy=18 * Game.scy),
            # @formatter:on
        ]),
        'decapite': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/retourne1.gif', xflip=True, tick=4,  mv=(-Game.chw, 0), dx=4 * Game.scx,   dy=14 * Game.scy),  # noqa
            frame(f'{subdir}/retourne1.gif', xflip=True, tick=5,  mv=(-Game.chw, 0), dx=4 * Game.scx,   dy=14 * Game.scy),  # noqa
            frame(f'{subdir}/retourne2.gif', xflip=True, tick=9,                                        dy=13 * Game.scy),  # noqa
            frame(f'{subdir}/retourne2.gif', xflip=True, tick=14, mv=(-Game.chw, 0),                    dy=13 * Game.scy),  # noqa
            frame(f'{subdir}/retourne3.gif', xflip=True, tick=15,                    dx=2 * Game.scx,   dy=14 * Game.scy),  # noqa
            frame(f'{subdir}/retourne3.gif', xflip=True, tick=19, mv=(-Game.chw, 0), dx=2 * Game.scx,   dy=14 * Game.scy),  # noqa
            frame(f'{subdir}/retourne3.gif', xflip=True, tick=24, mv=(-Game.chw, 0), dx=2 * Game.scx,   dy=14 * Game.scy),  # noqa
            frame(f'{subdir}/retourne3.gif', xflip=True, tick=29,                    dx=2 * Game.scx,   dy=14 * Game.scy),  # noqa
            frame(f'{subdir}/protegeH.gif',  xflip=True, tick=33,                                       dy=21 * Game.scy),  # noqa
            frame(f'{subdir}/cou2.gif',      xflip=True, tick=39,                                       dy=17 * Game.scy),  # noqa
            frame(f'{subdir}/cou3.gif',      xflip=True, tick=51,                    dx=-31 * Game.scx, dy=19 * Game.scy),  # noqa
            frame(f'{subdir}/cou2.gif',      xflip=True, tick=60,                                       dy=17 * Game.scy),  # noqa
            # @formatter:on
        ], actions=[
            Act(tick=15, act=Actions.snd, snd='decapite.ogg'),
        ]),
        'front': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/front1.gif', xflip=True, tick=5,                     dy=17 * Game.scy),
            frame(f'{subdir}/front2.gif', xflip=True, tick=23, dx=-5 * Game.scx,  dy=3 * Game.scy),
            frame(f'{subdir}/front3.gif', xflip=True, tick=30, dx=-22 * Game.scx, dy=18 * Game.scy),
            frame(f'{subdir}/front2.gif', xflip=True, tick=46, dx=-5 * Game.scx,  dy=3 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=5, act=Actions.snd, snd='epee.ogg'),
        ]),
        'retourne': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/retourne1.gif', xflip=True, tick=5,  mv=(-Game.chw, 0), dx=4 * Game.scx, dy=14 * Game.scy),
            frame(f'{subdir}/retourne2.gif', xflip=True, tick=10, mv=(-Game.chw, 0),                  dy=13 * Game.scy),
            frame(f'{subdir}/retourne3.gif', xflip=True, tick=18, mv=(-Game.chw, 0), dx=2 * Game.scx, dy=14 * Game.scy),
            # @formatter:on
        ]),
        'vainqueur': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=18,  dx=-4 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=35,  dx=-2 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur3.gif', xflip=True, tick=85,  dx=-0 * Game.scx, dy=10.1 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=100, dx=-2 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=101, dx=-4 * Game.scx, dy=17 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=102, act=Actions.stop),
        ]),
        'vainqueurKO': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/retourne1.gif',  xflip=True, tick=15,  dx=4 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/retourne2.gif',  xflip=True, tick=23,                    dy=13 * Game.scy),
            frame(f'{subdir}/retourne3.gif',  xflip=True, tick=30,  dx=2 * Game.scx,  dy=14 * Game.scy),
            frame(f'{subdir}/debout.gif',     xflip=True, tick=40,                    dy=18 * Game.scy),
            frame(f'{subdir}/marche3.gif',                tick=40,  dx=8 * Game.scx,  dy=18 * Game.scy),  # optional frame, see gestion on tick 35
            frame(f'{subdir}/marche3.gif',    xflip=True, tick=40,                    dy=18 * Game.scy),  # optional frame, see gestion on tick 35
            frame(f'{subdir}/debout.gif',     xflip=True, tick=55,                    dy=18 * Game.scy),
            frame(f'{subdir}/pied1.gif',      xflip=True, tick=70,  dx=-3 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied2.gif',      xflip=True, tick=75,  dx=-8 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/pied1.gif',      xflip=True, tick=100, dx=-3 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/debout.gif',     xflip=True, tick=105,                   dy=18 * Game.scy),
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=123, dx=-4 * Game.scx, dy=17 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=140, dx=-2 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur3.gif', xflip=True, tick=195,                   dy=10.1 * Game.scy),
            frame(f'{subdir}/vainqueur2.gif', xflip=True, tick=205, dx=-2 * Game.scx, dy=8 * Game.scy),
            frame(f'{subdir}/vainqueur1.gif', xflip=True, tick=231, dx=-4 * Game.scx, dy=17 * Game.scy),
            # @formatter:oon
        ], actions=[
            Act(tick=232, act=Actions.stop),
        ]),
        'touche1': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/touche2.gif', xflip=True, tick=1,                        dx=2 * Game.scx, dy=20 * Game.scy),  # noqa
            frame(f'{subdir}/touche2.gif', xflip=True, tick=5,  mv=(Game.chw,     0), dx=2 * Game.scx, dy=20 * Game.scy),  # noqa
            frame(f'{subdir}/touche1.gif', xflip=True, tick=10, mv=(2 * Game.chw, 0), dx=6 * Game.scx, dy=21 * Game.scy),  # noqa
            frame(f'{subdir}/touche2.gif', xflip=True, tick=20, mv=(Game.chw,     0), dx=2 * Game.scx, dy=20 * Game.scy),  # noqa
            frame(f'{subdir}/debout.gif',  xflip=True, tick=21, dy=18 * Game.scy),
            # @formatter:on
        ]),
        'tombe1': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/tombe1.gif', xflip=True, tick=1,                    dx=4 * Game.scx,  dy=21 * Game.scy),
            frame(f'{subdir}/tombe1.gif', xflip=True, tick=9,  mv=(Game.chw, 0), dx=4 * Game.scx,  dy=21 * Game.scy),
            frame(f'{subdir}/tombe2.gif', xflip=True, tick=15, mv=(Game.chw, 0), dx=10 * Game.scx, dy=58 * Game.scy),
            frame(f'{subdir}/tombe3.gif', xflip=True, tick=25,                   dx=8 * Game.scx,  dy=41 * Game.scy),
            frame(f'{subdir}/debout.gif', xflip=True, tick=27, mv=(Game.chw, 0),                   dy=18 * Game.scy),
            # @formatter:on
        ]),
        'mort': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/assis1.gif', xflip=True, tick=15, dy=26 * Game.scy),
            frame(f'{subdir}/mort2.gif',  xflip=True, tick=17, dx=-6 * Game.scx, dy=54 * Game.scy),
            frame(f'{subdir}/mort3.gif',  xflip=True, tick=18,                   dy=52 * Game.scy),  # manual, see vainqueurKO
            frame(f'{subdir}/mort4.gif',  xflip=True, tick=19, dx=-1 * Game.scx, dy=66 * Game.scy),  # manual, see vainqueurKO
            # @formatter:on
        ], actions=[
            Act(tick=1, act=Actions.snd, snd='mortKO.ogg'),
            Act(tick=17, act=Actions.stop),
        ]),
        'mortdecap': Animation(frames=[
            frame(f'{subdir}/decap1.gif', xflip=True, tick=35, dx=2 * Game.scx, dy=30 * Game.scy),
            frame(f'{subdir}/decap2.gif', xflip=True, tick=70, dx=-22 * Game.scx, dy=45 * Game.scy),
            frame(f'{subdir}/decap3.gif', xflip=True, tick=80, dx=-32 * Game.scx, dy=53 * Game.scy),
            frame(f'{subdir}/decap4.gif', xflip=True, tick=82, dx=-43 * Game.scx, dy=68 * Game.scy),
        ], actions=[
            Act(tick=1, act=Actions.snd, snd='mortdecap.ogg'),
            Act(tick=82, act=Actions.stop),
        ]),
        'mortgnome': Animation(frames=[
            frame(f'{subdir}/mort4.gif', xflip=True, tick=0, mv=(Game.chw / 12, 0)),
        ]),
        'mortdecapgnome': Animation(frames=[
            frame(f'{subdir}/decap4.gif', xflip=True, tick=0, mv=(Game.chw / 12, 0)),
        ]),
        'mortSORCIER': Animation(frames=[
            # @formatter:off
            frame(f'{subdir}/assis1.gif', xflip=True, tick=15, dy=26 * Game.scy),
            frame(f'{subdir}/mort2.gif',  xflip=True, tick=70, dx=-6 * Game.scx, dy=54 * Game.scy),
            frame(f'{subdir}/mort3.gif',  xflip=True, tick=85,                   dy=52 * Game.scy),
            frame(f'{subdir}/mort4.gif',  xflip=True, tick=87, dx=-1 * Game.scx, dy=66 * Game.scy),
            # @formatter:on
        ], actions=[
            Act(tick=88, act=Actions.stop),
        ]),
    }


def gnome():
    return {
        'gnome': Animation(frames=[
            frame('sprites/gnome1.gif', tick=5, mv=(Game.chw, 0)),
            frame('sprites/gnome2.gif', tick=11),
            frame('sprites/gnome3.gif', tick=17, mv=(Game.chw, 0)),
            frame('sprites/gnome4.gif', tick=23),
        ]),
    }


def feu():
    return {
        'feu_low': Animation(frames=[
            # @formatter:off
            frame('empty',            tick=55),  # loc 7
            frame('sprites/feu1.gif', tick=56, mv=(7    * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 14,    16.0
            frame('sprites/feu1.gif', tick=57, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 14.75, 16.5
            frame('sprites/feu1.gif', tick=58, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 15.5,  17.0
            frame('sprites/feu1.gif', tick=59, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 16.25, 17.5
            frame('sprites/feu1.gif', tick=60, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 17.0,  18.0
            frame('sprites/feu2.gif', tick=61, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 17.75, 18.5
            frame('sprites/feu2.gif', tick=62, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 18.5,  19.0
            frame('sprites/feu2.gif', tick=63, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 19.25, 19.5
            frame('sprites/feu2.gif', tick=65, mv=(0.75 * Game.chw, 0.5 * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 20.0,  20.0
            frame('sprites/feu3.gif', tick=66, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 20.75
            frame('sprites/feu3.gif', tick=67, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 21.5
            frame('sprites/feu3.gif', tick=68, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 22.25
            frame('sprites/feu3.gif', tick=70, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 23.0
            frame('sprites/feu1.gif', tick=71, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 23.75
            frame('sprites/feu1.gif', tick=72, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 24.5
            frame('sprites/feu1.gif', tick=73, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 25.25
            frame('sprites/feu1.gif', tick=75, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 26.0
            frame('sprites/feu2.gif', tick=76, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 26.75
            frame('sprites/feu2.gif', tick=77, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 27.5
            frame('sprites/feu2.gif', tick=78, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 28.25
            frame('sprites/feu2.gif', tick=80, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 29.0
            frame('sprites/feu3.gif', tick=81, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 29.75
            frame('sprites/feu3.gif', tick=82, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 30.5
            frame('sprites/feu3.gif', tick=83, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 31.25
            frame('sprites/feu3.gif', tick=85, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 32.0
            frame('sprites/feu1.gif', tick=86, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 32.75
            frame('sprites/feu1.gif', tick=87, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 33.5
            frame('sprites/feu1.gif', tick=88, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 34.25
            frame('sprites/feu1.gif', tick=89, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa loc 35.0
            frame('sprites/feu1.gif', tick=90, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa
            frame('sprites/feu1.gif', tick=91, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa
            frame('sprites/feu1.gif', tick=92, mv=(0.75 * Game.chw, 0   * Game.chh), colorkey=(255, 0, 255)),  # noqa
            # @formatter:on
        ], actions=[
            Act(tick=93, act=Actions.kill),
        ]),
        'feu_high': Animation(frames=[
            # @formatter:off
            frame('empty',            tick=135),  # loc 7
            frame('sprites/feu1.gif', tick=136, mv=(7    * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 14,
            frame('sprites/feu1.gif', tick=137, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 14.75,
            frame('sprites/feu1.gif', tick=138, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 15.5,
            frame('sprites/feu1.gif', tick=139, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 16.25,
            frame('sprites/feu1.gif', tick=140, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 17.0,
            frame('sprites/feu2.gif', tick=141, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 17.75,
            frame('sprites/feu2.gif', tick=142, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 18.5,
            frame('sprites/feu2.gif', tick=143, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 19.25,
            frame('sprites/feu2.gif', tick=145, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 20.0,
            frame('sprites/feu3.gif', tick=146, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 20.75
            frame('sprites/feu3.gif', tick=147, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 21.5
            frame('sprites/feu3.gif', tick=148, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 22.25
            frame('sprites/feu3.gif', tick=150, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 23.0
            frame('sprites/feu1.gif', tick=151, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 23.75
            frame('sprites/feu1.gif', tick=152, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 24.5
            frame('sprites/feu1.gif', tick=153, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 25.25
            frame('sprites/feu1.gif', tick=155, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 26.0
            frame('sprites/feu2.gif', tick=156, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 26.75
            frame('sprites/feu2.gif', tick=157, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 27.5
            frame('sprites/feu2.gif', tick=158, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 28.25
            frame('sprites/feu2.gif', tick=160, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 29.0
            frame('sprites/feu3.gif', tick=161, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 29.75
            frame('sprites/feu3.gif', tick=162, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 30.5
            frame('sprites/feu3.gif', tick=163, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 31.25
            frame('sprites/feu3.gif', tick=165, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 32.0
            frame('sprites/feu1.gif', tick=166, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 32.75
            frame('sprites/feu1.gif', tick=167, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 33.5
            frame('sprites/feu1.gif', tick=168, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 34.25
            frame('sprites/feu1.gif', tick=169, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa loc 35.0
            frame('sprites/feu1.gif', tick=170, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa
            frame('sprites/feu1.gif', tick=171, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa
            frame('sprites/feu1.gif', tick=172, mv=(0.75 * Game.chw, 0), colorkey=(255, 0, 255)),  # noqa
            # @formatter:on
        ], actions=[
            Act(tick=173, act=Actions.kill),
        ]),
    }


def sorcier():
    return {
        'debout': Animation(frames=[
            frame('sprites/drax1.gif', dy=23 * Game.scy),
        ]),
        'attaque': Animation(frames=[
            frame('sprites/drax1.gif', tick=50,  dy=23 * Game.scy),
            frame('sprites/drax2.gif', tick=60,  dy=23 * Game.scy),
            frame('sprites/drax1.gif', tick=130, dy=23 * Game.scy),
            frame('sprites/drax2.gif', tick=140, dy=23 * Game.scy),
            frame('sprites/drax1.gif', tick=141, dy=23 * Game.scy),
        ], actions=[
            Act(tick=50,  act=Actions.snd, snd='feu.ogg'),
            Act(tick=130, act=Actions.snd, snd='feu.ogg'),
            Act(tick=141, act=Actions.stop),
        ]),
    }

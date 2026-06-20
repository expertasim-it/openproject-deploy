import {makeScene2D, Rect, Txt, Img, Audio} from '@revideo/2d';
import {createRef, waitFor, useScene} from '@revideo/core';

export default makeScene2D('ad-template', function* (view) {
  const variables = useScene().variables;

  const headline = variables.get('headline', 'Your Headline Here')();
  const subhead = variables.get('subhead', 'Your subheading here')();
  const brandColor = variables.get('brandColor', '#1a73e8')();
  const backgroundClip = variables.get('backgroundClip', '')();
  const musicTrack = variables.get('musicTrack', '')();
  const durationSeconds = variables.get('durationSeconds', 20)();

  const bgRef = createRef<Rect>();
  const headlineRef = createRef<Txt>();
  const subheadRef = createRef<Txt>();

  view.add(
    <Rect ref={bgRef} width={'100%'} height={'100%'} fill={'#0a0a0a'} />
  );

  if (backgroundClip) {
    view.add(
      <Img
        src={backgroundClip}
        width={'100%'}
        height={'100%'}
        opacity={0.85}
      />
    );
  }

  if (musicTrack) {
    view.add(<Audio src={musicTrack} play={true} />);
  }

  view.add(
    <Rect
      width={'100%'}
      height={300}
      y={-200}
      fill={brandColor}
      opacity={0.85}
    />
  );

  view.add(
    <Txt
      ref={headlineRef}
      text={headline}
      fontSize={80}
      fontWeight={700}
      fill={'#ffffff'}
      y={-220}
      opacity={0}
    />
  );

  view.add(
    <Txt
      ref={subheadRef}
      text={subhead}
      fontSize={40}
      fill={'#ffffff'}
      y={-140}
      opacity={0}
    />
  );

  yield* waitFor(0.3);
  yield* headlineRef().opacity(1, 0.6);
  yield* subheadRef().opacity(1, 0.6);

  yield* waitFor(durationSeconds - 1.5);

  yield* headlineRef().opacity(0, 0.4);
  yield* subheadRef().opacity(0, 0.4);
});

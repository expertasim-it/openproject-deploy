import express from 'express';
import {renderVideo} from '@revideo/renderer';
import path from 'path';
import {fileURLToPath} from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(express.json());

const OUTPUT_DIR = '/app/output';

app.get('/health', (req, res) => {
  res.json({status: 'ok', service: 'video-pipeline'});
});

app.post('/render', async (req, res) => {
  const {
    headline,
    subhead,
    brandColor,
    backgroundClip,
    musicTrack,
    durationSeconds,
    runId
  } = req.body;

  if (!headline) {
    return res.status(400).json({error: 'headline is required'});
  }

  const outputFile = (runId || 'video_' + Date.now()) + '.mp4';

  try {
    const file = await renderVideo({
      projectFile: path.join(__dirname, 'src/project.ts'),
      variables: {
        headline: headline || 'Your Headline Here',
        subhead: subhead || '',
        brandColor: brandColor || '#1a73e8',
        backgroundClip: backgroundClip || '',
        musicTrack: musicTrack || '',
        durationSeconds: durationSeconds || 20
      },
      settings: {
        outFile: outputFile,
        outDir: OUTPUT_DIR,
        logProgress: true,
        ffmpeg: {
          ffmpegLogLevel: 'error'
        },
        puppeteer: {
          args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-accelerated-video-encode',
            '--disable-accelerated-video-decode',
            '--enable-unsafe-swiftshader',
            '--use-gl=swiftshader',
            '--disable-dev-shm-usage',
            '--disable-software-rasterizer'
          ]
        }
      }
    });

    res.json({
      status: 'success',
      output_file: outputFile,
      output_path: file
    });
  } catch (error) {
    res.status(500).json({error: error.message, stack: error.stack});
  }
});

app.get('/download/:filename', (req, res) => {
  const filePath = path.join(OUTPUT_DIR, req.params.filename);
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({error: 'File not found'});
  }
  res.sendFile(filePath);
});

app.get('/outputs', (req, res) => {
  const files = fs.readdirSync(OUTPUT_DIR).filter(f => f.endsWith('.mp4'));
  res.json({outputs: files});
});

app.listen(8770, '0.0.0.0', () => {
  console.log('Video pipeline API listening on port 8770');
});

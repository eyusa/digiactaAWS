from flask import Flask, render_template, request, redirect, url_for, send_from_directory, current_app, make_response, \
    jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
import m3u8
from urllib.parse import urlparse, urljoin


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


FFMPEG_BIN = "ffmpeg"
DOWNLOAD_FOLDER = 'files/download'

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def home():
    return "<html><h1>Welcome to HLS Editor API</h1><p>Post the editing related data to the following URI to start the editoing</p><p>  /process<p></html>"



@app.route('/process', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        app.logger.info(request)
        json_data = request.get_json(silent=False)
        app.logger.info("Json Data: " + str(json_data))
        filename = process_m3u8(json_data, app.config['DOWNLOAD_FOLDER'])
        ddir = os.path.join(current_app.root_path, app.config['DOWNLOAD_FOLDER'])
        return send_from_directory(directory=ddir, filename=filename, as_attachment=True)

    else:
        return redirect(url_for('home'))


#@app.route('/about')
def about():
    return render_template('about.html')


def process_m3u8(json_data, output_dir):
    if not json_data:
        json_data = {
            'variable_m3u8_url': 'https://emc-media-hls-bucket.s3.eu-central-1.amazonaws.com/Counter_10350/HLS/Counter_10350.m3u8',
            'get_content': 'video',
            'quality': 720,
            'time_in': "00:05:36",
            'time_out': "00:09:10"}

    m3u8_url = json_data.get('variable_m3u8_url')
    return_content_type = json_data.get('get_content')
    quality = json_data.get('quality')
    time_in = json_data.get('time_in')
    time_out = json_data.get('time_out')

    m3u8_file = m3u8.load(m3u8_url)

    playlist_to_process = None
    if m3u8_file.is_variant:
        for playlist in m3u8_file.playlists:
            if quality in playlist.stream_info.resolution:
                playlist_to_process = urljoin(m3u8_file.base_uri, playlist.uri)
                break
    else:
        raise InvalidUsage('specified m3u8 is not a root playlist', status_code=400)
        # return {'error': 'specified m3u8 is not a root playlist'}, 400

    if not playlist_to_process:
        raise InvalidUsage('specified quality not found in m3u8', status_code=400)
        # return {'error': 'specified quality not found in m3u8'}, 400

    a = urlparse(playlist_to_process)
    m3u8_file_name = os.path.basename(a.path)
    mp4_file_name = secure_filename('{}_{}_{}_{}.{}'.format(os.path.splitext(m3u8_file_name)[0], time_in, time_out,
                                                            return_content_type,
                                                            'mp4' if return_content_type == 'video' else 'aac'))
    output_file = os.path.join(output_dir, mp4_file_name)

    ffmpeg_cmd = [FFMPEG_BIN, '-hide_banner', '-y', '-i', playlist_to_process, '-ss', time_in, '-to', time_out,
                  '-c', 'copy', '-threads', '10', '-bsf:a', 'aac_adtstoasc',
                  output_file]

    if return_content_type == 'audio':
        ffmpeg_cmd[-2] = 'a'
        ffmpeg_cmd[-3] = '-map'

    app.logger.info('Command Being used: ' + " ".join(ffmpeg_cmd))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ffmpeg = subprocess.Popen(ffmpeg_cmd,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT
                              )

    while True:
        output = ffmpeg.stdout.readline().decode('utf-8').strip()
        app.logger.info(output)
        code = ffmpeg.poll()
        if code is None:
            if 'Press [q] to stop' in output:
                ffmpeg.stdin.write(b"t")
                ffmpeg.stdin.close()
                # break
        else:
            for lines in ffmpeg.stdout.readlines():
                app.logger.info(lines.decode('utf-8').strip())

            if code != 0:
                raise InvalidUsage('error converting', status_code=500)

            break

    return mp4_file_name


def from_hhmmss_to_sec(ts):
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(ts.split(":"))))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
    # response = process_m3u8(None, 'files/download')
    # print(response)

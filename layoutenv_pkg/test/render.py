from layoutenv.envs.layout_script import RenderLayoutModule
from layoutenv.envs.empty_layout import MessageBox
from piascomms.client import Client

source = "C:\\Users\\cursist\\Dorus\\ThesisResearch\\PiasExampleFiles\\temp\\goa1"
render = RenderLayoutModule(source, 14100, "Interactive")

user = MessageBox('Layout module')

if user.question('Do you want to sart the layout module?'):
    render.start_proces()

c = Client()

while not c.server_check():
    print('loading.....')
print('server live')

if user.question('Do you want to stop the layout module?'):
    render.kill_process()
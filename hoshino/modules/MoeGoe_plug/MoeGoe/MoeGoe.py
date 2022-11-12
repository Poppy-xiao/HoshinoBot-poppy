import sys, re
from torch import no_grad, LongTensor
import logging 
from .utils import *
from .models import SynthesizerTrn
from .text import text_to_sequence, _clean_text
from .mel_processing import spectrogram_torch

from scipy.io.wavfile import write
logging.getLogger('numba').setLevel(logging.WARNING)  

class MoeGoe():
    def intersperse(self,lst, item):
        result = [item] * (len(lst) * 2 + 1)
        result[1::2] = lst
        return result
    def ex_print(self,text,escape=False):
        if escape:
            print(text.encode('unicode_escape').decode())
        else:
            print(text)

    def get_text(self,text, hps, cleaned=False):
        if cleaned:
            text_norm = text_to_sequence(text, hps.symbols, [])
        else:
            text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
        if hps.data.add_blank:
            text_norm = self.intersperse(text_norm, 0)
        text_norm = LongTensor(text_norm)
        return text_norm

    def ask_if_continue(self,):
        while True:
            answer = input('Continue? (y/n): ')
            if answer == 'y':
                break
            elif answer == 'n':
                sys.exit(0)

    def print_speakers(self,speakers,escape=False):
        print('ID\tSpeaker')
        for id, name in enumerate(speakers):
            self.ex_print(str(id) + '\t' + name,escape)

    def get_speaker_id(self,message):
        speaker_id = input(message)
        try:
            speaker_id = int(speaker_id)
        except:
            print(str(speaker_id) + ' is not a valid ID!')
            sys.exit(1)
        return speaker_id

    def get_label_value(self,text, label, default, warning_name='value'):
        value=re.search(rf'\[{label}=(.+?)\]',text)
        if value:
            try:
                text=re.sub(rf'\[{label}=(.+?)\]','',text,1)
                value=float(value.group(1))
            except:
                print(f'Invalid {warning_name}!')
                sys.exit(1)
        else:
            value=default
        return value, text

    def get_label(self,text,label):
        if f'[{label}]' in text:
            return True,text.replace(f'[{label}]','')
        else:
            return False,text

    def __init__(self,id,readText,FileName):  
        if id <= 6:
            self.id = id
            self.modelPath  = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/yuzi/365_epochs.pth"
            self.configPath = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/yuzi/config.json"
        elif id <= 14 and id >6:
            self.id = id - 7
            self.modelPath  = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/Hamidashi/604_epochs.pth"
            self.configPath = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/Hamidashi/config.json"
        elif id <= 40 and id >14:
            self.id = id - 15
            self.modelPath  = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/Zeronotsukaima/616_epochs.pth"
            self.configPath = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/Zeronotsukaima/config.json"
        elif id <= 53 and id >40:
            self.id = id - 41
            self.modelPath  = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/DRACU-RIOT!/639_epochs.pth"
            self.configPath = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/DRACU-RIOT!/config.json"
        elif id <= 76 and id >53:
            self.id = id - 54
            self.modelPath  = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/CJKS/638_epochs.pth"
            self.configPath = "/home/poppy/workspace/HoshinoBot-poppy/hoshino/modules/MoeGoe_plug/MoeGoe/CJKS/config.json"
        self.outputPath = "/home/poppy/voice/" + FileName
        self.readText = readText
         
    def generate_voice(self):
        if '--escape' in sys.argv:
            escape=True
        else:
            escape=False
        
        model = self.modelPath
        config = self.configPath 
        
        hps_ms = get_hparams_from_file(config)
        n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
        n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
        speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
        use_f0 = hps_ms.data.use_f0 if 'use_f0' in hps_ms.data.keys() else False

        net_g_ms = SynthesizerTrn(
            n_symbols,
            hps_ms.data.filter_length // 2 + 1,
            hps_ms.train.segment_size // hps_ms.data.hop_length,
            n_speakers=n_speakers,
            **hps_ms.model)
        _ = net_g_ms.eval()
        load_checkpoint(model, net_g_ms)
        
        if n_symbols!=0:  
            text = self.readText 
            length_scale,text=self.get_label_value(text,'LENGTH',1,'length scale')
            noise_scale,text=self.get_label_value(text,'NOISE',0.667,'noise scale')
            noise_scale_w,text=self.get_label_value(text,'NOISEW',0.8,'deviation of noise')
            cleaned,text=self.get_label(text,'CLEANED') 
            stn_tst = self.get_text(text, hps_ms, cleaned=cleaned)
            
            # self.print_speakers(speakers,escape)
            speaker_id = self.id
            out_path = self.outputPath 
            with no_grad():
                x_tst = stn_tst.unsqueeze(0)
                x_tst_lengths = LongTensor([stn_tst.size(0)])
                sid = LongTensor([speaker_id])
                audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale, noise_scale_w=noise_scale_w, length_scale=length_scale)[0][0,0].data.cpu().float().numpy()
            write(out_path, hps_ms.data.sampling_rate, audio) 
            print('Successfully saved!') 
            return out_path
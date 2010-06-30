#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pygtk
import gtk
import sys, os, string, platform, time, shutil
import zipfile, random, urllib
import locale, gettext
import ConfigParser
config = ConfigParser.RawConfigParser()
if os.path.isfile('config.cfg'):
	pass
else:
	config.add_section('Lastpath')
	config.set('Lastpath', 'old', os.environ['HOME'])
	config.set('Lastpath', 'new', os.environ['HOME'])
	config.set('Lastpath', 'save', os.environ['HOME'])
	with open('config.cfg', 'wb') as configfile:
		config.write(configfile)

APP = 'Jigsaw-patcher'
DIR = 'locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext
TARGET_TYPE_URI_LIST = 80
dnd_list = [ ( 'text/uri-list', 0, TARGET_TYPE_URI_LIST ) ]

version = 0.1
'''
Select a temporary directory to work with the tbz
Select the xdelta binary path
'''
def selectbin():
    xdeltabin = {'xdeltal': './xdelta3.0v.x86-32.bin', 'xdeltaw': 'xdelta3.0u.x86-32.exe'}
    if os.name == 'posix':
		xdeltabin.update([('bin', xdeltabin['xdeltal'])])
    elif os.name == 'nt':
        xdeltabin.update([('bin', xdeltabin['xdeltaw'])])
    return xdeltabin

def selectdir():
    randomdir = str('%.9d' % (random.random() * 10000000000))
    if os.name == 'posix':
        temporaldir = os.path.join(os.environ['HOME'], '.Jigsaw-patcher')
    elif os.name == 'nt':
        temporaldir = os.path.join(os.environ['TMP'], '.Jigsaw-patcher')
    return temporaldir, randomdir


class Jigsaw():
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def motion_cb(self, wid, context, x, y, time):
		context.drag_status(gtk.gdk.ACTION_COPY, time)
		return True

    def drop_cb(self, wid, context, x, y, time):
    	print context
        context.finish(True, False, time)
        return True
    
    def get_file_path_from_dnd_dropped_uri(self, uri):
		# get the path to file
		path = ""
		if uri.startswith('file:\\\\\\'): # windows
			path = uri[8:] # 8 is len('file:///')
		elif uri.startswith('file://'): # nautilus, rox
			path = uri[7:] # 7 is len('file://')
		elif uri.startswith('file:'): # xffm
			path = uri[5:] # 5 is len('file:')

		path = urllib.url2pathname(path) # escape special chars
		path = path.strip('\r\n\x00') # remove \r\n and NULL

		return path

    def on_drag_data_received_old(self, widget, context, x, y, selection, target_type, timestamp):
		if target_type == TARGET_TYPE_URI_LIST:
			uri = selection.data.strip('\r\n\x00')
			uri_splitted = uri.split() # we may have more than one file dropped
			for uri in uri_splitted:
				path = self.get_file_path_from_dnd_dropped_uri(uri)
				self.chosenfile(path, 'fileold')


    def on_drag_data_received_new(self, widget, context, x, y, selection, target_type, timestamp):
		if target_type == TARGET_TYPE_URI_LIST:
			uri = selection.data.strip('\r\n\x00')
			uri_splitted = uri.split() # we may have more than one file dropped
			for uri in uri_splitted:
				path = self.get_file_path_from_dnd_dropped_uri(uri)
				self.chosenfile(path, 'filenew')

    def displayerror(self, type):
        self.status_bar.push(2, _('Error, please try again.'))
        lbl = { 'createbat': _('.bat could not be written for some reason.'), 'createsh': _('.sh could not be written for some reason.')}
        lbl.update([('createxdeltadir', _('Destination folder does not exist.'))])
        lbl.update([('createxdeltamiss', _('One of the needed files to create the patch not found.'))])
        lbl.update([('createmiss', _('One of the needed files is missing.'))])
        lbl.update([('createzipfile', _('.zip file could not be written'))])
        title = { 'createbat': _('.bat creation failed'), 'createsh': _('.sh creation failed')} 
        title.update([('createxdeltadir', _('.xdelta creation failed'))])
        title.update([('createxdeltamiss', _('.xdelta creation failed'))])
        title.update([('createmiss', _('.xdelta creation failed'))])
        title.update([('createzipfile', _('.zip creation failed'))])
        buttons = gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT
        display = gtk.Dialog(title[type], None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, buttons=buttons)
        label = gtk.Label(lbl[type])
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(label, False, False, 30)
        label.show()
        display.vbox.pack_start(hbox, False, False, 30) 
        hbox.show()
        display.show()
        if display.run() == gtk.RESPONSE_ACCEPT:
            display.destroy()

    def btncreatezip(self, widget):
        if ('OFF', 'ON')[widget.get_active()] == 'ON':
            self.createzipbool = True
            self.optframeif.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        else:
            self.createzipbool = False
            self.optframeif.set_shadow_type(gtk.SHADOW_ETCHED_OUT)

    def btncreatezipsel(self, widget, data=None):
        if ('OFF', 'ON')[widget.get_active()] == 'ON':
            self.createzipsel = data

    def createbat(self, xdeltabinw, filebat, fileold, filenew, xdelta):
        try:
            data = ['@echo off\n']
            data.append('echo %s created with Jigsaw-patcher. http://code.google.com/p/jigsaw-patcher/ \n' % os.path.basename(filebat))
            data.append('echo Patch to use in Microsoft Windows. \n')
            data.append('echo.\n')
            data.append('echo Old file: %s. \n' % fileold)
            data.append('echo New file: %s. \n' % filenew)
            data.append('echo Applying patch... \n')
            data.append('%s -d -s "%s" "%s" "%s" \n' % (xdeltabinw, fileold, xdelta, filenew))
            data.append('echo Patch applied.\n')
            data.append('pause\n')
            file = open(filebat, 'w')
            for i in data:
                file.write(i)
            file.close()
        except:
            self.displayerror('createbat')
            return False

    def createsh(self, xdeltabinl, filesh, fileold, filenew, xdelta):
        try:
			data = ['#!/bin/bash\n\n']
			data.append('echo "%s created with Jigsaw-patcher. http://code.google.com/p/jigsaw-patcher/"\n' % os.path.basename(filesh))
			data.append('echo "Patch to use in GNU/Linux."\n')
			data.append('echo ')
			data.append('echo "Old file %s. "\n' % fileold)
			data.append('echo "New file: %s. "\n' % filenew)
			data.append('echo "Applying patch... "\n')
			data.append('%s -d -s "%s" "%s" "%s" \n' % (xdeltabinl, fileold, xdelta, filenew))
			data.append('echo "Patch applied."\n')
			data.append('read -p "Press a key to exit..."\n')
			data.append('exit 0\n')
			data.append('fi\n')
			file = open(filesh, 'w')
			for i in data:
				file.write(i)
			file.close()
        except:
            self.displayerror('createsh')
            return False

    def createxdelta(self, xdeltabin, fileold, filenew, xdelta):
        if os.path.isfile(xdeltabin) and os.path.isfile(fileold) and os.path.isfile(filenew):
            if os.path.isdir(os.path.dirname(xdelta)):
                os.popen('%s -f -e -s "%s" "%s" "%s"' % (xdeltabin, fileold, filenew, xdelta))
                return True
            else:
                self.displayerror('createxdeltadir')
                return False
        else:
            self.displayerror('createxdeltamiss')
            return False

    def createzipfile(self, workdir, pathfiles):
        try: 
            zip = zipfile.ZipFile(pathfiles['xdeltapath'].strip('.xdelta') + '.zip', 'w')
            for file in os.listdir(workdir):
                zip.write(os.path.join(workdir, file), file)
            zip.close()
            return True
        except:
            self.displayerror('createzipfile')
            return False

    def createtemp(self, tempdir, randomdir):   
        try: 
            os.makedirs(os.path.join(tempdir,randomdir))
            return True
        except:
            self.displayerror('createtemp')
            return False
        
    def cleartemp(self, tempdir, randomdir):
        for file in os.listdir(os.path.join(tempdir, randomdir)):
            os.remove(os.path.join(tempdir,randomdir,file))
        os.rmdir(os.path.join(tempdir,randomdir))
#        try:
        os.rmdir(tempdir)
           
    def createpatch(self, widget):
        for i in ['xdelta', 'filenew', 'fileold']:
            try:
                if i not in self.pathfiles:
                    pass
            except:
                self.displayerror('createmiss')
                return False
        xdeltabin = selectbin()
        if not os.path.isfile(os.path.join('data', xdeltabin['bin'])):
            self.displayerror('createxdeltabinmiss')
            return False
        self.status_bar.push(3, _('Creating patch'))
        if self.createzipbool:
            tempdir = selectdir()
            workdir = os.path.join(tempdir[0], tempdir[1])
            batchpattern = self.pathfiles['xdeltaname'].strip('.xdelta')
            self.createtemp(tempdir[0], tempdir[1])
            self.createxdelta(os.path.join('data', xdeltabin['bin']), self.pathfiles['fileoldpath'], self.pathfiles['filenewpath'], os.path.join(workdir, self.pathfiles['xdeltaname']))
            if self.createzipsel == _('GNU/Linux'):
                shutil.copy(os.path.join('data', xdeltabin['xdeltal']), os.path.join(workdir,xdeltabin['xdeltal32']))
                self.createsh(xdeltabin['xdeltal'], os.path.join(workdir, batchpattern + '.sh'), \
                                self.pathfiles['fileoldname'], self.pathfiles['filenewname'], self.pathfiles['xdeltaname'])
            elif self.createzipsel == _('Microsoft Windows'):
                shutil.copy(os.path.join('data', xdeltabin['xdeltaw']), os.path.join(workdir,xdeltabin['xdeltaw']))
                self.createbat(xdeltabin['xdeltaw'], os.path.join(workdir, batchpattern + '.bat'), \
                                self.pathfiles['fileoldname'], self.pathfiles['filenewname'], self.pathfiles['xdeltaname'])
            elif self.createzipsel == _('GNU/Linux and Microsoft Windows'):
                shutil.copy(os.path.join('data', xdeltabin['xdeltal']), os.path.join(workdir,xdeltabin['xdeltal']))
                shutil.copy(os.path.join('data', xdeltabin['xdeltaw']), os.path.join(workdir,xdeltabin['xdeltaw']))
                self.createsh(xdeltabin['xdeltal'], os.path.join(workdir, batchpattern + '.sh'), \
                                self.pathfiles['fileoldname'], self.pathfiles['filenewname'], self.pathfiles['xdeltaname'])
                self.createbat(xdeltabin['xdeltaw'], os.path.join(workdir, batchpattern + '.bat'), \
                                self.pathfiles['fileoldname'], self.pathfiles['filenewname'], self.pathfiles['xdeltaname'])
            self.createhelp(os.path.join(workdir, 'readme.txt'))
            self.createzipfile(workdir, self.pathfiles)
            self.cleartemp(tempdir[0],tempdir[1])
        else:
            self.createxdelta(os.path.join('data', xdeltabin['bin']), self.pathfiles['fileoldpath'], self.pathfiles['filenewpath'], self.pathfiles['xdeltapath'])
        self.status_bar.push(3, _('Patch created succesfully'))

    def createhelp(self, filename):
        data = ['readme.txt\n']
        data.append(_('Patch created with Jigsaw-patcher, thanks to xdelta3.\n\n'))
        data.append(_('To patch under Microsoft Windows run the file with the extension: .bat\n'))
        data.append(_('To patch under GNU/Linux run the file with the extension: .sh\n\n'))
        data.append(_('It is necessary to put the original file in the same folder, with the patch files.\n\n'))
        data.append(_('Visit the web project @ http://code.google.com/p/jigsaw-patcher/\n'))
        file = open(filename, 'w')
        for i in data:
            file.write(i)
        file.close()   

    def filechoose(self, widget, type):
        name = ''
        config = ConfigParser.RawConfigParser()
        config.read('config.cfg')
        if type == 'xdelta':
            win_title = _('Save as..')
            win_action = gtk.FILE_CHOOSER_ACTION_SAVE
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK)
            filter_name = [_('xdelta patch (.xdelta)'), _('zip archive (.zip)'), _('Any supported file (*)')]
            pattern = ['*.xdelta', '*.zip', '*']
            pathtolast = config.get('Lastpath', 'save')
        elif type == 'fileold' :
            win_action = gtk.FILE_CHOOSER_ACTION_OPEN
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK)
            win_title = _('Open old file..')
            filter_name = [_('Any supported file (*)'), _('Video MKV (.mkv)')]
            pattern = ['*', '*.mkv']
            pathtolast = config.get('Lastpath', 'old')
        elif type == 'filenew':
            win_action = gtk.FILE_CHOOSER_ACTION_OPEN
            buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK)
            win_title = _('Open new file..')
            filter_name = [_('Any supported file (*)'), _('Video MKV (.mkv)')]
            pattern = ['*', '*.mkv']
            pathtolast = config.get('Lastpath', 'new')
        dialog = gtk.FileChooserDialog(win_title, None, win_action, buttons )
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(pathtolast)

        for i in xrange(len(filter_name)):
            filter = gtk.FileFilter()
            filter.set_name(filter_name[i])
            filter.add_pattern(pattern[i])
            dialog.add_filter(filter)
        
        if type == 'xdelta':
            dialog.set_do_overwrite_confirmation(True)

        if dialog.run() == gtk.RESPONSE_OK:
            name = dialog.get_filename()
        elif dialog.run() == gtk.RESPONSE_CANCEL:
            name = _('Not Selected')
        dialog.destroy()
    
    	self.chosenfile(name, type)
    	
    def chosenfile(self, name, type):
        config = ConfigParser.RawConfigParser()
        config.read('config.cfg')
        if type == 'xdelta':
            if name == _('Not Selected'):
                pass
            else:
                basename = os.path.basename(name)
                if basename.find('.xdelta') == -1:
                    basename = basename + '.xdelta'
                    name = name + '.xdelta'
                try:
                    self.pathfiles.update([('xdeltapath', name)])
                except AttributeError:
                    self.pathfiles = {'xdeltapath': name}
                self.pathfiles.update([('xdeltaname', basename)])
                self.ent_xdelta.set_text(self.pathfiles['xdeltaname'])
                self.tooltips.set_tip(self.ent_xdelta, self.pathfiles['xdeltapath'])
                config.set('Lastpath', 'save', os.path.dirname(name))

        elif type == 'fileold':
            if name == _('Not Selected'):
                pass
            else:                
                basename = os.path.basename(name)
                try:
                    self.pathfiles.update([('fileoldpath', name)])
                except AttributeError:
                    self.pathfiles = {'fileoldpath': name}
                self.pathfiles.update([('fileoldname', basename)])

                self.ent_fileold.set_text(self.pathfiles['fileoldname'])
                self.tooltips.set_tip(self.ent_fileold, self.pathfiles['fileoldpath'])
                config.set('Lastpath', 'old', os.path.dirname(name))
        
        elif type == 'filenew':
            if name == _('Not Selected'):
                pass
            else:                
                basename = os.path.basename(name)
                try:
                    self.pathfiles.update([('filenewpath', name)])
                except AttributeError:
                    self.pathfiles = {'filenewpath': name}
                self.pathfiles.update([('filenewname', basename)])

                self.ent_filenew.set_text(self.pathfiles['filenewname'])
                self.tooltips.set_tip(self.ent_filenew, self.pathfiles['filenewpath'])
                config.set('Lastpath', 'new', os.path.dirname(name))
        with open('config.cfg', 'wb') as configfile:
            config.write(configfile)


    def __init__(self):
        # Window properties
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect('delete_event', self.delete_event)
        window.set_border_width(0)
        window.set_title(_('Jigsaw-patcher (xdelta gui)'))
        icon = gtk.gdk.pixbuf_new_from_file(os.path.join('data', 'Jigsaw-patcher.png'))
        window.set_icon(icon)

        frame = gtk.Frame(_('Patch creator'))
        frame.set_label_align(0.5,0.5)
        frame.set_border_width(00)
        vboxbig = gtk.VBox(False, 0)
        hboxbig = gtk.HBox(False, 0)
        vboxin = gtk.VBox(False, 0)
        hboxin = gtk.HBox(False, 0)

        self.status_bar = gtk.Statusbar()
        self.status_bar.push(1, _('Ready'))
        self.tooltips = gtk.Tooltips()


        #################### Patch file Start #####################
        tblapply = gtk.Table(6,3, False)
        ########## fileold row
        btn_fileold = gtk.Button('...', gtk.STOCK_OPEN)
        btn_fileold.connect('clicked', self.filechoose, 'fileold')
        tblapply.attach(btn_fileold, 2, 3, 0, 1, yoptions=0, xoptions=2)
        btn_fileold.show()

        lbl_fileold = gtk.Label(_('Old file:'))
        lbl_fileold.set_justify(gtk.JUSTIFY_RIGHT)
        tblapply.attach(lbl_fileold, 0, 1, 0, 1)
        lbl_fileold.show()

        self.ent_fileold = gtk.Entry()
        self.ent_fileold.set_text(_('Not Selected'))
        self.ent_fileold.set_width_chars(50)
        self.ent_fileold.set_alignment(0.5)
        self.ent_fileold.set_editable(False)
        self.ent_fileold.drag_dest_set( gtk.DEST_DEFAULT_MOTION |
                  gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                  dnd_list, gtk.gdk.ACTION_COPY)
        self.ent_fileold.connect('drag_motion', self.motion_cb)
#        self.ent_fileold.connect('drag_drop', self.drop_cb)
        self.ent_fileold.connect('drag_data_received', self.on_drag_data_received_old)
        tblapply.attach(self.ent_fileold, 1, 2, 0, 1)
        self.ent_fileold.show()
        ########## filenew row
        btn_filenew = gtk.Button('...', gtk.STOCK_OPEN)
        btn_filenew.connect('clicked', self.filechoose, 'filenew')
        tblapply.attach(btn_filenew, 2, 3, 1, 2, yoptions=0, xoptions=2)
        btn_filenew.show()

        lbl_filenew = gtk.Label(_('New file:'))
        tblapply.attach(lbl_filenew, 0, 1, 1, 2)
        lbl_filenew.show()

        self.ent_filenew = gtk.Entry()
        self.ent_filenew.set_text(_('Not Selected'))
        tblapply.attach(self.ent_filenew, 1, 2, 1, 2)
        self.ent_filenew.set_width_chars(50)
        self.ent_filenew.set_alignment(0.5)
        self.ent_filenew.set_editable(False)
        self.ent_filenew.drag_dest_set( gtk.DEST_DEFAULT_MOTION |
                  gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                  dnd_list, gtk.gdk.ACTION_COPY)
        self.ent_filenew.connect('drag_motion', self.motion_cb)
#        self.ent_fileold.connect('drag_drop', self.drop_cb)
        self.ent_filenew.connect('drag_data_received', self.on_drag_data_received_new)
        self.ent_filenew.show()

        ########## xdelta row
        btn_xdelta = gtk.Button('...', gtk.STOCK_SAVE_AS)
        btn_xdelta.connect('clicked', self.filechoose, 'xdelta')
        tblapply.attach(btn_xdelta, 2, 3, 2, 3, yoptions=0, xoptions=2)
        btn_xdelta.show()

        lbl_xdelta = gtk.Label(_('Patch file:'))
        lbl_xdelta.set_justify(gtk.JUSTIFY_LEFT)
        tblapply.attach(lbl_xdelta, 0, 1, 2, 3, gtk.EXPAND, 0, 0)
        lbl_xdelta.show()

        self.ent_xdelta = gtk.Entry()
        self.ent_xdelta.set_text(_('Not Selected'))
        tblapply.attach(self.ent_xdelta, 1, 2, 2, 3)
        self.ent_xdelta.set_width_chars(50)
        self.ent_xdelta.set_alignment(0.5)
        self.ent_xdelta.set_editable(False)
        self.ent_xdelta.show()

        separator = gtk.HSeparator()
        separator.set_size_request(30, 30)
        tblapply.attach(separator, 0, 4, 3, 4)
        separator.show()

        opttable = gtk.Table(4, 4, False)
        optframe = gtk.Frame(_('Options'))
        optframe.set_label_align(0.5,0.5)
        zipcheck = gtk.CheckButton(_('Create zip'))
        zipcheck.connect('toggled', self.btncreatezip)
        opthbox = gtk.HBox(False, 0)
        radiolin = gtk.RadioButton(None, _('GNU/Linux'))
        radiolin.connect('toggled', self.btncreatezipsel, _('GNU/Linux'))
        radiowin = gtk.RadioButton(radiolin, _('Microsoft Windows'))
        radiowin.connect('toggled', self.btncreatezipsel, _('Microsoft Windows'))
        radiolinwin = gtk.RadioButton(radiowin, _('GNU/Linux and Microsoft Windows'))
        radiolinwin.set_active(True)
        self.createzipsel = _('GNU/Linux and Microsoft Windows')
        radiolinwin.connect('toggled', self.btncreatezipsel, _('GNU/Linux and Microsoft Windows'))
        self.optframeif = gtk.Frame(_('If zip..'))
        zipcheck.set_active(True)
        self.optframeif.set_border_width(10)
        self.optframeif.set_label_align(0.5,0.5)
        self.optframeif.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        opthboxif = gtk.HBox(False, 0)
        optvboxif = gtk.VBox(False, 0)

        optvboxif.pack_start(radiolin, False, False, 0)
        optvboxif.pack_start(radiowin, False, False, 0)
        optvboxif.pack_start(radiolinwin, False, False, 0)
        opthboxif.pack_start(optvboxif, False, False, 5)
        optvboxif.show()
        self.optframeif.add(opthboxif)
        opthboxif.show()
        opttable.attach(self.optframeif, 1, 2, 0, 3)
        self.optframeif.show()


        endbox = gtk.HBox(False, 0)
        opttable.attach(zipcheck, 0, 1, 0, 1)
        zipcheck.show()
        radiolinwin.show()
        radiolin.show()
        radiowin.show()
        optframe.add(opttable)
        opttable.show()
        opthbox.pack_start(optframe, False, False, 0)
        optframe.show()
        endbox.pack_start(opthbox, False, False, 0)
        opthbox.show()
        
        hboxbtn = gtk.HBox(False, 0)
        vboxbtn = gtk.VBox(False, 0)
        btncreatepatch = gtk.Button(_('Create'))
        btncreatepatch.connect('clicked', self.createpatch)
        hboxbtn.pack_start(btncreatepatch, False, False, 30)
        btncreatepatch.show()
        vboxbtn.pack_end(hboxbtn, False, False, 20)
        hboxbtn.show()
        endbox.pack_end(vboxbtn, False, False, 00)
        vboxbtn.show()

        tblapply.attach(endbox, 0, 3, 4, 5)
        endbox.show()
        
        hboxin.pack_start(tblapply, False, False, 15)
        tblapply.show()
        vboxin.pack_start(hboxin, False, False, 15)
        hboxin.show()
        frame.add(vboxin)
        vboxin.show()
        hboxbig.pack_start(frame, False, False, 15)
        frame.show()
        vboxbig.pack_start(hboxbig, False, False, 15)
        hboxbig.show()
        vboxbig.pack_start(self.status_bar, False, False, 0)
        self.status_bar.show()
        window.add(vboxbig)
        vboxbig.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == '__main__':
    Jigsaw()
    main()

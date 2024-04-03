# Py macro UI actions graph
Started as simplest AutoHotkey alternative, this script was generalised and extended for possible future reuse.

It will be especially useful if:
- Main part of the automated routine are icon or button clicks with detection based just on the element images
- Image detection is still expected to work on other scales (UI 100%, 150%) and with color invariance (light, dark theme)
- Macro execution routine is not linear nor known in advance, also involve random branching (with simultaneous execution attempts until any of branches succeed)  
- Custom action extensions are required which are easier  to write on Python rather than with AutoHotkey
- A personal preference is just against AutoHotkey due to ~10 Virustotal detections on multiple versions  

Just to give an idea how it can be used, current default macro is enabling Hoxx or Setup VPN browser extensions automatically.
That's just one common routine I noticed to be fun to try. Feel free to propose better default macro though.  

Also an easy graphical debug is used which shows how macro chain was fired: 

<p float="right">
  <img src="docs/Debug_view_example.png?raw=1" width="436" float="none" alt=""/>
</p>  

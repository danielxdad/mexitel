#!/bin/bash
while true; do
	wget --no-cache --spider --timeout=10 --user-agent=Mozilla/5.0 "https://mexitel.sre.gob.mx/citas.webportal/pages/private/cita/registro/registroCitasPortalExtranjeros.jsf?nuevaCitaPortal=true";
	sleep 10;
done

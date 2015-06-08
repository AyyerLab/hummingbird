import analysis.event
import analysis.beamline
import analysis.hitfinding
import analysis.pixel_detector
import ipc   

state = {
    'Facility': 'LCLS',
    'LCLS/DataSource': ipc.mpi.get_source(['/data/rawdata/LCLS/cxi/cxic9714/xtc/e419-r0203-s01-c00.xtc', 
                                           '/data/rawdata/LCLS/cxi/cxic9714/xtc/e419-r0204-s01-c00.xtc'])
}

def onEvent(evt):
    analysis.beamline.printPulseEnergy(evt['pulseEnergies'])
    analysis.beamline.printPhotonEnergy(evt['photonEnergies'])
    print "EPICS photon energy = %g eV" %(evt['parameters']['SIOC:SYS0:ML00:AO541'].data)
    analysis.pixel_detector.printStatistics(evt['photonPixelDetectors'])
    analysis.pixel_detector.printStatistics(evt['ionTOFs'])
    #print "Rank = ", ipc.mpi.rank, analysis.event.printID(evt['eventID'])
    # Count Nr. of Photons
    #analysis.pixel_detector.totalNrPhotons(evt,"photonPixelDetectors", "CCD")

    # Simple hitfinding (Count Nr. of lit pixels)
    #analysis.hitfinding.countPhotons(evt, "photonPixelDetectors", "CCD", aduThreshold=0.5, hitscoreThreshold=10)

    analysis.event.printProcessingRate()
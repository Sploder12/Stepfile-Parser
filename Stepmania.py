COLUMNS = {"4": ['L', 'D', 'U', 'R'],
            "5": ['L', 'D', 'C', 'U', 'R'],
            "6": ['L', 'Q', 'D', 'U', 'W', 'R'],
            "7": ['L', 'Q', 'D', 'C', 'U', 'W', 'R'],
            "8": ['L', 'D', 'U', 'R', 'Q', 'W', 'T', 'Y'],
            "9": ['L', 'D', 'U', 'R', 'C', 'Q', 'W', 'T', 'Y'],
            "10": ['L', 'D', 'C', 'U', 'R', 'Q', 'W', 'V', 'T', 'Y']}

NOTE_TYPE_4TH = 0
NOTE_TYPE_8TH = 1
NOTE_TYPE_12TH = 2
NOTE_TYPE_16TH = 3
NOTE_TYPE_24TH = 4
NOTE_TYPE_32ND = 5
NOTE_TYPE_48TH = 6
NOTE_TYPE_64TH = 7
NOTE_TYPE_192ND = 8
NOTE_TYPE_INVALID = 9

ROWS_PER_MEASURE = 192

fields_array = ['title',
            'subtitle',
            'artist',
            'titletranslit',
            'subtitletranslit',
            'artisttranslit',
            'credit',
            'banner',
            'background',
            'cdtitle',
            'music',
            'offset',
            'samplestart',
            'samplelength',
            'bpms',
            'stops',
            'freezes',
            'notes']

fields_number = ['offset',
            'samplestart',
            'samplelength']

standard_type = {'dance-single':4, 
            'pump-single':5,
            'dance-solo':6,
            'pump-halfdouble':6,
            'dance-double':8,
            'dance-couple':8,
            'dance-routine':8,
            'pump-double':10,
            'pump-couple':10}

colors_dict = {NOTE_TYPE_4TH:"red",
            NOTE_TYPE_8TH:"blue",
            NOTE_TYPE_12TH:"purple",
            NOTE_TYPE_16TH:"yellow",
            NOTE_TYPE_24TH:"pink",
            NOTE_TYPE_32ND:"orange",
            NOTE_TYPE_48TH:"cyan",
            NOTE_TYPE_64TH:"green",
            NOTE_TYPE_192ND:"white",
            NOTE_TYPE_INVALID:"white"}

def getNoteType(noteIndex):
            if (noteIndex % (ROWS_PER_MEASURE / 4) == 0):
                return NOTE_TYPE_4TH
            elif (noteIndex % (ROWS_PER_MEASURE / 8) == 0):
                return NOTE_TYPE_8TH
            elif (noteIndex % (ROWS_PER_MEASURE / 12) == 0):
                return NOTE_TYPE_12TH
            elif (noteIndex % (ROWS_PER_MEASURE / 16) == 0):
                return NOTE_TYPE_16TH
            elif (noteIndex % (ROWS_PER_MEASURE / 24) == 0):
                return NOTE_TYPE_24TH
            elif (noteIndex % (ROWS_PER_MEASURE / 32) == 0):
                return NOTE_TYPE_32ND
            elif (noteIndex % (ROWS_PER_MEASURE / 48) == 0):
                return NOTE_TYPE_48TH
            elif (noteIndex % (ROWS_PER_MEASURE / 64) == 0):
                return NOTE_TYPE_64TH
            else:
                return NOTE_TYPE_INVALID

def dict2list(dict):
    caster = []
    for pair in dict:
        caster.append([float(list(pair.keys())[0]), float(list(pair.values())[0])])
    return caster

def bpm_at_beat_index(curBeat, startIdx, bpms):
    curBeat = round(curBeat, 3)

    bpm = startIdx
    length = len(bpms)

    for i in range(startIdx, length):
        if(bpms[i][0] > curBeat):
            break
        
        bpm = i

    return bpm

def finalizeNoteData(noteData, bpms, stops, offset):

    columnCnt = noteData["type"]
    columnMap = COLUMNS[str(columnCnt)]

    offset *= -1000
    out = {"data":noteData, "columns":columnCnt}

    notes = []
    holds = []
    mines = []

    pre_notes = []
    pre_mines = []
    pre_holds = [[],[],[],[],[],[],[],[],[],[]]

    currentBeat = 0
    currentTime = 0

    measureArr = noteData["data"].split(',')
    measureCnt = len(measureArr)

    notebarOffset = 0
    rowVal = 0

    lastBPMIndex = 0
    lastStopIndex = 0
    lastStop = None

    warpStart = -1
    isWarping = False
    
    for currentMeasure in range(measureCnt):
        rowVal = currentMeasure * ROWS_PER_MEASURE
        
        measure = measureArr[currentMeasure]
        notebarOffset = 0

        barsPerMeasure = int(len(measure)/columnCnt)
        measureBeat = currentMeasure * 4

        for currentNoteBar in range(barsPerMeasure):
            currentBeat = measureBeat + ((currentNoteBar / barsPerMeasure) * 4)

            lastBPMIndex = bpm_at_beat_index(currentBeat, lastBPMIndex, bpms)
            currentBPM = bpms[lastBPMIndex][1]

            if(len(stops) > 0 and lastStopIndex < len(stops)):
                if(lastStop is None):
                    lastStop = stops[0]
                
                while(lastStop[0] <= currentBeat):
                    currentTime += lastStop[1] * 1000
                    lastStopIndex += 1
                    if(lastStopIndex >= len(stops)):
                        break

                    lastStop = stops[lastStopIndex]


            if(currentBPM < 0 and not isWarping):
                warpStart = currentTime
                isWarping = True
            
            if(not isWarping):
                for column in range(columnCnt):
                    noteStr = measure[notebarOffset + column]

                    if(noteStr == "0"):
                        continue

                    if(noteStr == "1" or noteStr == "2" or noteStr == "4"):
                        if(noteStr == "2" or noteStr == "4"):
                            pre_holds[column] = len(pre_notes)

                        noteColor = colors_dict[getNoteType(currentNoteBar * (ROWS_PER_MEASURE / barsPerMeasure))]
                        pre_notes.append([int(currentTime), columnMap[column], noteColor])
                    elif (noteStr == "3"):
                        if(pre_holds[column] is not None):
                            holdStart = pre_holds[column]
                            holdStartData = pre_notes[holdStart]
                            pre_notes[holdStart].append(currentTime - holdStartData[0])
                            pre_holds[column] = []
                    elif (noteStr == "M"):
                        pre_mines.append([int(currentTime), columnMap[column]])
    
            notebarOffset += columnCnt
            
            rowUpdates = int(ROWS_PER_MEASURE/barsPerMeasure)
            for row in range(rowUpdates):
                rowVal += 1
                currentBeat = measureBeat + (((currentNoteBar / barsPerMeasure) + (row / ROWS_PER_MEASURE)) * 4)
                lastBPMIndex = bpm_at_beat_index(currentBeat, lastBPMIndex, bpms)
                currentBPM = bpms[lastBPMIndex][1]

                if(currentBPM < 0 and not isWarping):
                    warpStart = currentTime
                    isWarping = True

                msBeatIncrement = 1000 / (currentBPM / 60)
                currentTime += ((4 / ROWS_PER_MEASURE) * msBeatIncrement)
            
            if isWarping:
                if(int(currentTime) >= int(warpStart)):
                    warpStart = -1
                    isWarping = False


    for elm in pre_notes:
        elm[0] = (offset + elm[0]) / 1000
        notes.append(elm)

        if(len(elm) > 3):
            elm[3] /= 1000
            holds.append(elm)

    for elm in pre_mines:
        elm[0] = (offset + elm[0]) / 1000
        mines.append(elm)

    out["data"]["notes"] = sorted(notes)
    out["data"]["holds"] = sorted(holds)
    out["data"]["mines"] = sorted(mines)
    out["data"]["data"] = "" #clear the big gross stuff

    return out

def load(fileName):
    file = open(fileName)
    buffer = file.read()

    tmpdata = {"notes":[]}
    tmpbpms = []
    tmpstops = []

    matches = []
    sI = 0
    sE = 0
    
    while True:
        try:
            sI = buffer.index('#', sE)
            sE = buffer.index(';', sI)
        except ValueError:
            break

        if (sI >= 0 and sE > sI):
            mstr = buffer[sI:sE]
            splitt = mstr.index(':', 0)
            key = mstr[1:splitt].lower()
            value = mstr[splitt + 1:]

            matches.append({key:value})
        else:
            break

    for match in matches:
        key = list(match.keys())[0]
        if not (key in fields_array):
            continue
        if(key == "bpms" or key == "stops" or key == "freezes"):
            lst = []
            subs = match[key].split(',')
            for dat in subs:
                try:
                    indx = dat.index('=')
                    lst.append({dat[:indx]: dat[indx + 1:]})
                except:
                    continue
            tmpdata[key] = lst
        elif(key == "notes"):
            tmpnotes = {}

            noteVals = match[key].split(':')
            for trim in range(len(noteVals)):     
                noteVals[trim] = noteVals[trim][1:].strip()

            tmpnotes["type"] = standard_type[noteVals[0]]
            tmpnotes["desc"] = noteVals[1]
            tmpnotes["class"] = noteVals[2]
            tmpnotes["class_color"] = noteVals[2]
            tmpnotes["difficulty"] = noteVals[3]
            tmpnotes["radar_values"] = noteVals[4]

            notesDat = noteVals[5].split('\n')
            noteStr = ""
            for dat in notesDat:
                try:
                    commentIdx = dat.index('/')
                    
                    dat = dat[:commentIdx]
                except:
                    pass
                dat = dat.strip()
                noteStr += dat
            
            tmpnotes["data"] = noteStr

            tmpnotes["arrows"] = noteStr.count('1')
            tmpnotes["holds"] = noteStr.count('2')
            tmpnotes["mines"] = noteStr.count('M')

            tmpdata["notes"].append(tmpnotes)
        else:
            if key in fields_number:
                tmpdata[key] = float(match[key])
            else:
                tmpdata[key] = match[key]

    tmpbpms = tmpdata["bpms"]
    caster = dict2list(tmpbpms)
    if(len(caster) <= 0):
        caster.append([0, 60])

    tmpbpms = sorted(caster)

    try:
        tmpstops = tmpdata["stops"]
    except:
        try:
            tmpstops = tmpdata["freezes"]
        except:
            pass

    caster = dict2list(tmpstops)
    tmpstops = sorted(caster)

    #@TODO finalize notes via adding timings
    for i in range(len(tmpdata["notes"])):
        tmpdata["notes"][i] = finalizeNoteData(tmpdata["notes"][i], tmpbpms, tmpstops, tmpdata["offset"])
    
    tmpdata["stepauthor"] = tmpdata["credit"]
    print(tmpdata["notes"][0]["data"]["notes"][-1])
    
    return tmpdata


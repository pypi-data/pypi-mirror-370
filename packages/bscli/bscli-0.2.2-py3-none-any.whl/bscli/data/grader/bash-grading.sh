#!/bin/bash

next() {
    local cwd=${PWD##*/}
    unset found
    unset nwd

    for x in ../*/; do
        if [ -v found ] ; then
            nwd=$x
            break
        elif [ ${x#../} == ${cwd}/ ] ; then
            found=1
        fi
    done

    if [ -v nwd ] ; then
        cd $nwd
        grade_submission
    else
        echo Finished grading
    fi
}

remaining() {
    local cwd=${PWD##*/}

    if [ -d ../../submissions ] ; then
        total=`ls -ld ../*/ | wc -l`
        graded=0

        for x in ../*/; do
            if [ ${x#../} == ${cwd}/ ] ; then
                break
            else
                graded=$((graded+1))
            fi
        done

        echo You have $((total-graded)) submissions left to grade
    fi
}

numsubmissions() {
    if [ -d ../../submissions ] ; then
        echo You have `ls -ld ../*/ | wc -l` submissions to grade
    fi
}

cursubmission() {
    local cwd=${PWD##*/}

    if [ -d ../../submissions ] ; then
        count=0

        for x in ../*/; do
            count=$((count+1))
            if [ ${x#../} == ${cwd}/ ] ; then
                echo This is submission number $count
                break
            fi
        done
    fi
}

goto_submission() {
    local cwd=${PWD##*/}

    if [ -d ../../submissions ] ; then
        count=0

        for x in ../*/; do
            count=$((count+1))
            if [ "$count" -eq "$1" ] ; then
                cd $x
                echo Moved to submission number $count
                break
            fi
        done
    fi
}

startgrading() {
    if [ -r data/course_grading_function.sh ] && [ ! -x data/course_grading_function.sh ] ; then
        chmod +x data/course_grading_function.sh
    fi

    if [ -d submissions ] ; then
        echo Found `ls -1d submissions/*/ | wc -l` submissions
        cd `ls -1d submissions/*/ | head -n 1`
        grade_submission
    else
        echo No submissions folder found
    fi
}

finishgrading() {
    if [ -r ../../data/upload-virtualenv.sh ] ; then
        cd ../../data

        if [ ! -x upload-virtualenv.sh ] ; then
            chmod +x upload-virtualenv.sh
        fi

        ./upload-virtualenv.sh
    else
        echo upload-virtualenv.sh not found, are you in the wrong folder?
    fi
}

grade_generic() {
    PDF_COUNT=`find . -iname '*.pdf' | wc -l`
    TEXT_COUNT=`find . -type f -name '*' -exec file --mime-type --print0 {} \; | grep -Ea 'text/.*' | cut -f 1 -d '' | grep -v './feedback.txt' | wc -l`
    PCAP_COUNT=`find . -iname '*.pcap' | wc -l`
    PCAPNG_COUNT=`find . -iname '*.pcapng' | wc -l`

    # open pdf file(s)
    if [ $PDF_COUNT -gt 0 ] ; then
        find . -iname '*.pdf' -exec zathura --fork --mode=fullscreen "{}" \;
    fi

    # open packet captures in wireshark
    if [ $PCAP_COUNT -gt 0 ] ; then
        find . -iname '*.pcap' -exec bash -c 'wireshark -r "{}" & disown' \;
    fi
    if [ $PCAPNG_COUNT -gt 0 ] ; then
        find . -iname '*.pcapng' -exec bash -c 'wireshark -r "{}" & disown' \;
    fi

    # open feedback file in a forked GUI vim instance
    vim -g feedback.txt

    sleep 0.2s

    # maximize GUI vim window
    VIM_WINDOW=`wmctrl -l | grep -E 'feedback.txt.* - VIM.*$' | cut -f 1 -d ' '`
    wmctrl -i -b add,maximized_vert,maximized_horz -r $VIM_WINDOW

    # open user text files in vim
    if [ $TEXT_COUNT -gt 0 ] ; then
        find . -type f -name '*' -exec file --mime-type --print0 {} \; | grep -Ea 'text/.*' | cut -f 1 -d '' | grep -v './feedback.txt' | xargs -I % echo \"%\" | xargs -o vim -o
    fi
}

grade_submission() {
    echo Now grading: ${PWD##*/}
    echo

    # trigger specialized grading script for course if one exists, use generic grading function otherwise
    if [ -x ../../data/course_grading_function.sh ]; then
        ../../data/course_grading_function.sh
    else
        grade_generic
    fi
}

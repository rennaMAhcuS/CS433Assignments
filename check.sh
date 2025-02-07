for i in {0..3}; do
    echo "Test $i"
    echo "expected: $(cat outputs/output$i.txt)"
    echo "got: $(python3 solve.py inputs/input$i.txt)"
    echo "-------------------------------------"
done

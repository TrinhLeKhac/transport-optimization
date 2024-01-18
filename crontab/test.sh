for argument in "$@"
do
  key=$(echo $argument | cut --fields 1 --delimiter='=')
  value=$(echo $argument | cut --fields 2 --delimiter='=')

  case "$key" in
    --mode|-m)        mode="$value" ;;
    --get-data|-g)    get_data="$value" ;;
    --run-date|-r)    run_date="$value" ;;
    *)
  esac
done

if [ -z "$3" ]
  then
    run_date=$(date +%F)
fi

echo "We'll running script with mode $mode, get data by $get_data and run on date $run_date"


import edgarquery

def main():

    argp = argparse.ArgumentParser(description="collect EDGAR
    companyticker json files and convert them to csv")

    argp.add_argument('--file', required=False, help="json file to process")
    argp.add_argument('--odir', default='/tmp',
                help="where to deposit the fileѕ")

    args = argp.parse_args()

    tc = edgarquery.tickerstocsv.EDGARTickerstoCSV()

    tc.urljstocsv(odir=args.odir)

main()

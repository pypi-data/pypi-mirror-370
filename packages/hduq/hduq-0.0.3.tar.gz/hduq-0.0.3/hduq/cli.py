# import argparse
# from hduq.cgh import *

# def parse_mode(s):
#     parts = s.split(',')
#     if len(parts) != 2:
#         raise argparse.ArgumentTypeError('Expected two comma-separated integers, e.g. 0,1')
#     try:
#         n, m = int(parts[0]), int(parts[1])
#     except ValueError:
#         raise argparse.ArgumentTypeError('Mode orders must be integers')
#     return n, m

# def main():
#     parser = argparse.ArgumentParser(description='HDUQ CLI tool')
#     subparsers = parser.add_subparsers(dest='command', required=True)

#     cgh_parser = subparsers.add_parser('cgh', help='Generate CGH')
#     cgh_parser.add_argument('--hg', type=parse_mode, help='HG mode orders, e.g. 0,1', action='append')
#     cgh_parser.add_argument('--pmx', choices=['p', 'm', 'plus', 'minus'], help="PM x mode 'orders', (p)lus or (m)inus", action='append')
#     cgh_parser.add_argument('--pmy', choices=['p', 'm', 'plus', 'minus'], help="PM y mode 'orders', (p)lus or (m)inus", action='append')
#     cgh_parser.add_argument('--nx', type=int, required=True, help='Relative spatial frequency nx')
#     cgh_parser.add_argument('--ny', type=int, required=True, help='Relative spatial frequency ny')
#     cgh_parser.add_argument('--sigma', type=float, required=True, help='Characteristic width')
#     cgh_parser.add_argument('--output', type=str, default='./Untitled CGH.bmp', help='Output file path to save the CGH')

#     args = parser.parse_args()


#     if args.command == 'cgh':

#         def define_modes(hg=None, pmx=None, pmy=None):
#             hg_modes = hg or [] 
#             pmx_modes = pmx or []
#             pmy_modes = pmy or []

#             if not hg_modes and not pmx_modes and not pmy_modes:
#                 print('You must specify at least one mode by --hg, --pmx or --pmy')
#                 exit(1)

#             modes = []
#             for n, m in hg_modes:
#                 modes.append(HG(n, m))

#             for pmx in pmx_modes:
#                 modes.append(PMx(pmx))

#             for pmy in pmy_modes:
#                 modes.append(PMy(pmy))

#             return modes

#         modes = define_modes(args.hg, args.pmx, args.pmy)
#         try:
#             CGH(args.sigma, *modes, nx=args.nx, ny=args.ny).save(args.output)
#         except Exception as e:
#             print(f'{type(e).__name__}: {e}')
#             exit(1)
#         print(f'Saved CGH to {args.output}')


# if __name__ == '__main__':
#     main()

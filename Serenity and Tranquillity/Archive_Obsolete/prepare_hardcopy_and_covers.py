from __future__ import annotations

from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
PRINT_SOURCE = BASE / "Serenity_and_Tranquillity_Print_Interior.pdf"
DIGITAL_SOURCE = BASE / "Serenity_and_Tranquillity_Digital_Readable.pdf"
WRAP_JPG = BASE / "Cover_Spread_From_Original_A5_299p.jpg"
FRONT_JPG = BASE / "Cover_Front_OnlineStore_From_Original.jpg"


def parse_pdf(path: Path) -> tuple[bytes, dict[int, bytes], list[int], int, int]:
    data = path.read_bytes()
    starts = list(re.finditer(rb"(?m)^([0-9]+) 0 obj\r?\n", data))
    objects: dict[int, bytes] = {}
    for i, match in enumerate(starts):
        end = data.find(b"endobj", match.end())
        if end < 0:
            continue
        objects[int(match.group(1))] = data[match.end():end].strip()
    catalog_id = next(k for k,v in objects.items() if b"/Type /Catalog" in v)
    catalog = objects[catalog_id]
    pages_id = int(re.search(rb"/Pages\s+(\d+)\s+0\s+R", catalog).group(1))
    kids = re.search(rb"/Kids\s*\[(.*?)\]", objects[pages_id], re.S).group(1)
    page_ids = [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", kids)]
    outlines_match = re.search(rb"/Outlines\s+(\d+)\s+0\s+R", catalog)
    outlines_id = int(outlines_match.group(1)) if outlines_match else 0
    return data, objects, page_ids, catalog_id, outlines_id


def stream_bytes(obj: bytes) -> bytes:
    m = re.search(rb"\bstream\r?\n(.*?)\r?\nendstream\b", obj, re.S)
    if not m:
        raise ValueError("PDF content object has no stream")
    return m.group(1)


def page_content(objects: dict[int, bytes], page_id: int) -> tuple[bytes, float, float, dict[str,int], list[int]]:
    page = objects[page_id]
    media = re.search(rb"/MediaBox\s*\[\s*[-\d.]+\s+[-\d.]+\s+([-\d.]+)\s+([-\d.]+)\s*\]", page)
    width, height = float(media.group(1)), float(media.group(2))
    content_id = int(re.search(rb"/Contents\s+(\d+)\s+0\s+R", page).group(1))
    fonts = {name.decode(): int(ref) for name,ref in re.findall(rb"/(Times-Roman|Times-Bold|Times-Italic)\s+(\d+)\s+0\s+R", page)}
    annot_match = re.search(rb"/Annots\s*\[(.*?)\]", page, re.S)
    annots = [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", annot_match.group(1))] if annot_match else []
    return stream_bytes(objects[content_id]), width, height, fonts, annots


def annotation_info(obj: bytes) -> tuple[tuple[float,float,float,float], int] | None:
    rect = re.search(rb"/Rect\s*\[\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\]", obj)
    dest = re.search(rb"/Dest\s*\[\s*(\d+)\s+0\s+R\s+/Fit\s*\]", obj)
    if not rect or not dest:
        return None
    return tuple(float(rect.group(i)) for i in range(1,5)), int(dest.group(1))


def outline_entries(objects: dict[int,bytes], outlines_id: int) -> list[tuple[bytes,int]]:
    if not outlines_id:
        return []
    root = objects[outlines_id]
    m = re.search(rb"/First\s+(\d+)\s+0\s+R", root)
    if not m:
        return []
    current = int(m.group(1)); result=[]; seen=set()
    while current and current not in seen:
        seen.add(current)
        obj=objects[current]
        title=re.search(rb"/Title\s+(<[^>]+>|\([^)]*\))",obj)
        dest=re.search(rb"/Dest\s*\[\s*(\d+)\s+0\s+R\s+/Fit\s*\]",obj)
        if title and dest:
            result.append((title.group(1),int(dest.group(1))))
        nxt=re.search(rb"/Next\s+(\d+)\s+0\s+R",obj)
        current=int(nxt.group(1)) if nxt else 0
    return result


def write_pdf(path: Path, source: Path, placements: list[list[tuple[int,float,float,float]]], page_box: tuple[float,float], replace_first_image: Path | None = None) -> int:
    _, old, old_pages, _, old_outline_id = parse_pdf(source)
    old_page_index={pid:i for i,pid in enumerate(old_pages)}
    source_fonts: dict[str,int] = {}
    page_specs=[]
    for pid in old_pages:
        content,w,h,fonts,annots=page_content(old,pid)
        source_fonts.update(fonts)
        page_specs.append((content,w,h,annots))

    objects: list[bytes | None] = []
    def reserve() -> int:
        objects.append(None); return len(objects)
    def add(obj: bytes | str) -> int:
        if isinstance(obj,str): obj=obj.encode("ascii")
        objects.append(obj); return len(objects)

    catalog_id=reserve(); pages_id=reserve()
    font_ids={name:add(old[ref]) for name,ref in source_fonts.items()}

    form_ids: dict[int,int] = {}
    if replace_first_image is None:
        form_source_indices=range(len(old_pages))
    else:
        form_source_indices=range(1,len(old_pages))
    for src_i in form_source_indices:
        content,w,h,_=page_specs[src_i]
        fresources=" ".join(f"/{name} {ref} 0 R" for name,ref in font_ids.items())
        form=(f"<< /Type /XObject /Subtype /Form /FormType 1 /BBox [0 0 {w:.2f} {h:.2f}] "
              f"/Resources << /Font << {fresources} >> >> /Length {len(content)} >>\nstream\n").encode("ascii")+content+b"\nendstream"
        form_ids[src_i]=add(form)

    image_id=0
    if replace_first_image:
        jpeg=replace_first_image.read_bytes()
        # Front cover art is exported as baseline JPEG, RGB, 1800 x 2520.
        image_id=add(b"<< /Type /XObject /Subtype /Image /Width 1800 /Height 2520 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length "+str(len(jpeg)).encode()+b" >>\nstream\n"+jpeg+b"\nendstream")

    page_ids=[reserve() for _ in placements]
    outline_root=reserve()
    old_outlines=outline_entries(old,old_outline_id)
    outline_ids=[reserve() for _ in old_outlines]
    link_objects: list[list[int]]=[[] for _ in placements]
    # Map every source page to the new sheet/page that contains it.
    source_to_output: dict[int,int]={}
    for out_i, placement in enumerate(placements):
        for src_i,_,_,_ in placement:
            source_to_output[src_i]=out_i

    pw,ph=page_box
    for out_i,placement in enumerate(placements):
        xobjects=[]; ops=[]
        if replace_first_image is not None and out_i==0:
            xobjects.append(f"/Cover {image_id} 0 R")
            ops.extend(["q",f"{pw:.2f} 0 0 {ph:.2f} 0 0 cm /Cover Do","Q"])
        else:
            for part_i,(src_i,scale,xoff,yoff) in enumerate(placement):
                name=f"/P{part_i+1}"
                xobjects.append(f"{name} {form_ids[src_i]} 0 R")
                ops.extend(["q",f"{scale:.8f} 0 0 {scale:.8f} {xoff:.3f} {yoff:.3f} cm {name} Do","Q"])
                src_page_id=old_pages[src_i]
                for annot_id in page_specs[src_i][3]:
                    info=annotation_info(old[annot_id])
                    if not info:
                        continue
                    (x1,y1,x2,y2),dest_page_id=info
                    dest_i=old_page_index.get(dest_page_id)
                    if dest_i is None or dest_i not in source_to_output:
                        continue
                    rect=[xoff+scale*x1,yoff+scale*y1,xoff+scale*x2,yoff+scale*y2]
                    dest_new_page=page_ids[source_to_output[dest_i]]
                    annotation=(f"<< /Type /Annot /Subtype /Link /Rect [{rect[0]:.2f} {rect[1]:.2f} {rect[2]:.2f} {rect[3]:.2f}] "
                                f"/Border [0 0 0] /Dest [{dest_new_page} 0 R /Fit] >>")
                    link_objects[out_i].append(add(annotation))
        stream="\n".join(ops).encode("ascii")
        contents_id=add(b"<< /Length "+str(len(stream)).encode()+b" >>\nstream\n"+stream+b"\nendstream")
        xobjdict=" ".join(xobjects)
        annots=f" /Annots [{ ' '.join(f'{i} 0 R' for i in link_objects[out_i]) }]" if link_objects[out_i] else ""
        objs=f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {pw:.2f} {ph:.2f}] /Resources << /XObject << {xobjdict} >> >> /Contents {contents_id} 0 R{annots} >>"
        objects[page_ids[out_i]-1]=objs.encode("ascii")

    for i,((title,old_dest),obj_id) in enumerate(zip(old_outlines,outline_ids)):
        old_index=old_page_index.get(old_dest)
        if old_index is None or old_index not in source_to_output:
            continue
        prev=f" /Prev {outline_ids[i-1]} 0 R" if i else ""
        nxt=f" /Next {outline_ids[i+1]} 0 R" if i+1<len(outline_ids) else ""
        dest=page_ids[source_to_output[old_index]]
        objects[obj_id-1]=f"<< /Title {title.decode('ascii')} /Parent {outline_root} 0 R /Dest [{dest} 0 R /Fit]{prev}{nxt} >>".encode("ascii")
    if outline_ids:
        objects[outline_root-1]=f"<< /Type /Outlines /First {outline_ids[0]} 0 R /Last {outline_ids[-1]} 0 R /Count {len(outline_ids)} >>".encode("ascii")
    else:
        objects[outline_root-1]=b"<< /Type /Outlines >>"
    kids=" ".join(f"{pid} 0 R" for pid in page_ids)
    objects[pages_id-1]=f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")
    objects[catalog_id-1]=f"<< /Type /Catalog /Pages {pages_id} 0 R /Outlines {outline_root} 0 R /PageMode /UseOutlines >>".encode("ascii")
    title_hex="536572656E69747920616E64205472616E7175696C6C697479"
    info_id=add(f"<< /Title <{title_hex}> /Author <50726F662E204A6F686E736F6E2041676861726573652045676F6E6D77616E> /Creator <436F646578> >>")
    out=bytearray(b"%PDF-1.7\n%\xE2\xE3\xCF\xD3\n"); offsets=[0]
    for n,obj in enumerate(objects,1):
        offsets.append(len(out)); out.extend(f"{n} 0 obj\n".encode()); out.extend(obj or b"<<>>"); out.extend(b"\nendobj\n")
    xref=len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(objects)+1} /Root {catalog_id} 0 R /Info {info_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(out)
    return len(page_ids)


def get_page_ids(pdf: Path) -> list[int]:
    return parse_pdf(pdf)[2]


if __name__ == "__main__":
    _, src_objects, src_pages, _, _ = parse_pdf(PRINT_SOURCE)
    _, _, page_w, page_h, _, _ = None, None, 0, 0, None, None
    _,srcw,srch,_,_=page_content(src_objects,src_pages[0])
    a5w,a5h=420.96,595.32
    scale=min(a5w/srcw,a5h/srch)
    xoff=(a5w-srcw*scale)/2
    yoff=(a5h-srch*scale)/2
    single=[[(i,scale,xoff,yoff)] for i in range(len(src_pages))]
    single_count=write_pdf(BASE/"Serenity_and_Tranquillity_Print_Interior_A5_Single.pdf",PRINT_SOURCE,single,(a5w,a5h))
    spread=[]
    half=841.92/2
    for i in range(0,len(src_pages),2):
        parts=[(i,scale,xoff,yoff)]
        if i+1<len(src_pages): parts.append((i+1,scale,half+xoff,yoff))
        spread.append(parts)
    spread_count=write_pdf(BASE/"Serenity_and_Tranquillity_Hardcopy_A5_2up.pdf",PRINT_SOURCE,spread,(841.92,595.32))
    # Full-wrap print cover: existing supplied art, re-sized only to match the A5 spread/bleed dimensions.
    cover_jpg=WRAP_JPG.read_bytes()
    # Build a one-page raster PDF directly, retaining the supplied back/spine/front art and barcode.
    cover_w=(2*5.8472+0.7475+0.25)*72
    cover_h=(8.268+0.25)*72
    image_id=1; content_id=2; page_id=3; pages_id=4; catalog_id=5; info_id=6
    content=f"q {cover_w:.2f} 0 0 {cover_h:.2f} 0 0 cm /Cover Do Q".encode("ascii")
    objs=[
        b"<< /Type /XObject /Subtype /Image /Width 3807 /Height 2555 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length "+str(len(cover_jpg)).encode()+b" >>\nstream\n"+cover_jpg+b"\nendstream",
        b"<< /Length "+str(len(content)).encode()+b" >>\nstream\n"+content+b"\nendstream",
        f"<< /Type /Page /Parent 4 0 R /MediaBox [0 0 {cover_w:.2f} {cover_h:.2f}] /Resources << /XObject << /Cover 1 0 R >> >> /Contents 2 0 R >>".encode("ascii"),
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Catalog /Pages 4 0 R >>",
        b"<< /Title <5072696E7420436F76657220537072656164> /Author <50726F662E204A6F686E736F6E2041676861726573652045676F6E6D77616E> >>",
    ]
    path=BASE/"Serenity_and_Tranquillity_Print_Cover_A5_299p_Corrected.pdf"
    data=bytearray(b"%PDF-1.7\n%\xE2\xE3\xCF\xD3\n"); offsets=[0]
    for n,obj in enumerate(objs,1): offsets.append(len(data)); data.extend(f"{n} 0 obj\n".encode()); data.extend(obj); data.extend(b"\nendobj\n")
    xref=len(data); data.extend(f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(f"trailer\n<< /Size {len(objs)+1} /Root 5 0 R /Info 6 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()); path.write_bytes(data)
    # Replace only the digital PDF's existing cover page; all text/interior pages are imported unchanged.
    _,dig_objects,dig_pages,_,_=parse_pdf(DIGITAL_SOURCE)
    dig_placements=[[(i,1.0,0.0,0.0)] for i in range(len(dig_pages))]
    digital_count=write_pdf(BASE/"Serenity_and_Tranquillity_Digital_Readable_CoverCorrected.pdf",DIGITAL_SOURCE,dig_placements,(595.28,841.89),FRONT_JPG)
    notes=f'''# Hard-copy and cover correction files

The existing editable manuscript, original digital PDF, original print interior, and original cover files were left unchanged. These are additional, versioned deliverables.

- `Serenity_and_Tranquillity_Print_Interior_A5_Single.pdf`: {single_count} individual A5 pages, scaled from the existing 6 x 9 in print interior without changing its text.
- `Serenity_and_Tranquillity_Hardcopy_A5_2up.pdf`: {spread_count} A4 landscape sheets with two facing A5 pages per sheet, matching the supplied example's two-up layout. The final sheet has a blank right-hand page.
- `Serenity_and_Tranquillity_Print_Cover_A5_299p_Corrected.pdf`: one-page full spread made from the supplied cover image, preserving its illustrations, text, spine artwork, barcode, and ISBN.
- `Serenity_and_Tranquillity_Digital_Readable_CoverCorrected.pdf`: the digital PDF with only its first cover page replaced by a front-only crop of the supplied cover; all later pages retain their source content.
- `Cover_Front_OnlineStore_From_Original.jpg`: front-only image for ebook store cover upload.

The reference PDF is A4 landscape and places two facing pages side by side; its logical pages are A5-sized. The one-up PDF is the usual page-by-page file for a print provider. The two-up file is for a printer that wants the same spread arrangement as the reference.

The supplied cover PNG is 1536 x 1024 pixels. It has been enlarged to fit the A5 wrap; enlargement does not add detail, so the effective image resolution is about 120 dpi. The text and barcode were retained exactly as supplied. The A5 wrap uses a 0.7475 in spine assumption for 299 pages on cream paper. A printer's stock may need a different spine width.
'''
    (BASE/"Hardcopy_and_Cover_Correction_Notes.md").write_text(notes,encoding="utf-8")
    print(f"A5 single-page interior: {single_count} pages")
    print(f"A4 landscape two-up spreads: {spread_count} sheets")
    print("A5 print cover, online front cover, and cover-corrected digital PDF created.")
